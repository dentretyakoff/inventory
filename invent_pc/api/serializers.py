from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from invent_pc.comps.models import (Comp, Department, Disk, Host, ItemsChoices,
                                    Monitor, Ram, VirtualMachine, VMAdapter,
                                    WebCamera)


class DiskSerializer(serializers.ModelSerializer):
    """Сериализатор дисков."""

    class Meta:
        model = Disk
        fields = ('model', 'capacity', 'serial_number')


class RamSerializer(serializers.ModelSerializer):
    """Сериализатор оперативной памяти."""

    class Meta:
        model = Ram
        fields = ('model', 'capacity', 'serial_number')


class MonitorSerializer(serializers.ModelSerializer):
    """Сериализатор мониторов."""

    class Meta:
        model = Monitor
        fields = ('model', 'manufacturer', 'serial_number')


class WebCameraSerializer(serializers.ModelSerializer):
    """Сериализатор веб-камер."""

    class Meta:
        model = WebCamera
        fields = ('model',)


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    "Кастомный SlugRelatedField для создания объекта."

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        if queryset.model.__name__ == 'Department':
            data = data.upper()
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            return self.get_queryset().create(**{self.slug_field: data})
        except (TypeError, ValueError):
            self.fail('invalid')


class CompSerializer(serializers.ModelSerializer):
    """Сериализатор компов."""
    disks = DiskSerializer(many=True, required=False)
    rams = RamSerializer(many=True, required=False)
    monitors = MonitorSerializer(many=True, required=False)
    department = CreatableSlugRelatedField(
        queryset=Department.objects.all(),
        slug_field='name')
    web_camera = CreatableSlugRelatedField(
        queryset=WebCamera.objects.all(),
        slug_field='model')

    class Meta:
        model = Comp
        fields = '__all__'

    def create(self, validated_data):
        disks_data = validated_data.pop('disks', [])
        rams_data = validated_data.pop('rams', [])
        monitors_data = validated_data.pop('monitors', [])

        # Создаем компьютер
        comp, created = Comp.objects.update_or_create(
            pc_name=validated_data.get('pc_name'),
            defaults=validated_data)

        received_items = [
            {'model': Disk, 'data': disks_data},
            {'model': Ram, 'data': rams_data},
            {'model': Monitor, 'data': monitors_data},
        ]

        # Создаем или обновляем оборудование имеющее серийные номера
        for item in received_items:
            m = item['model']
            for item_data in item['data']:
                m.objects.update_or_create(
                    comp=comp,
                    **item_data,
                    defaults={
                        'uninstall_date': None,
                        'status': ItemsChoices.INSTALLED})

            exists_items = m.objects.filter(comp=comp,
                                            status=ItemsChoices.INSTALLED)
            sn_items = [sn.get('serial_number') for sn in item['data']]

            # Помечаем потерянное оборудование
            for exists_item in exists_items:
                if exists_item.serial_number not in sn_items:
                    exists_item.uninstall_date = timezone.now()
                    exists_item.status = ItemsChoices.LOST
                    exists_item.save()

        return comp


class VMAdapterSerializer(serializers.ModelSerializer):
    """Сериализатор адаптеров виртуальных машин."""

    class Meta:
        model = VMAdapter
        fields = ('mac', 'vlan')


class VirtualMachineSerializer(serializers.ModelSerializer):
    """Сериализатор виртуальных машин."""
    adapters = VMAdapterSerializer(many=True, source='adapter')

    class Meta:
        model = VirtualMachine
        fields = ('name', 'uptime', 'vm_id', 'adapters')


class HostCreateSerializer(serializers.ModelSerializer):
    """Сериализатор хостов. Создает связь с виртуальными машинами."""
    vms = VirtualMachineSerializer(many=True)

    class Meta:
        model = Host
        fields = '__all__'

    def create(self, validated_data):
        vms_data = validated_data.pop('vms')

        host, created = Host.objects.get_or_create(**validated_data)

        vms_list = []
        for vm_data in vms_data:
            adapters = vm_data.pop('adapter')
            macs = [adapter.get('mac') for adapter in adapters]
            vm, _ = VirtualMachine.objects.update_or_create(
                name=vm_data.get('name'),
                vm_id=vm_data.get('vm_id'),
                defaults={'uptime': vm_data.get('uptime')})
            vms_list.append(vm)
            vm.adapter.exclude(mac__in=macs).delete()
            for adapter in adapters:
                adapter, _ = VMAdapter.objects.get_or_create(**adapter, vm=vm)
        host.vms.set(vms_list)
        return host
