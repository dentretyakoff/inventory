"""Переопределяем кодировку в библиотеке pywinrm для корректного отображения
кириллицы.
codepage = 65001
"""
import winrm


class CustomProtocol(winrm.protocol.Protocol):
    def open_shell(
        self,
        i_stream: str = "stdin",
        o_stream: str = "stdout stderr",
        working_directory: str = None,
        env_vars: dict[str, str] = None,
        noprofile: bool = False,
        codepage: int = 65001,  # Установка кодировки UTF-8
        lifetime: int = None,
        idle_timeout: str = None,
    ) -> str:
        return super().open_shell(
            i_stream=i_stream,
            o_stream=o_stream,
            working_directory=working_directory,
            env_vars=env_vars,
            noprofile=noprofile,
            codepage=codepage,
            lifetime=lifetime,
            idle_timeout=idle_timeout,
        )


class CustomSession(winrm.Session):
    def __init__(self, target, auth, **kwargs):
        username, password = auth
        self.url = self._build_url(
            target,
            kwargs.get('transport', 'plaintext')
        )
        self.protocol = CustomProtocol(
            self.url,
            username=username,
            password=password,
            **kwargs
        )
