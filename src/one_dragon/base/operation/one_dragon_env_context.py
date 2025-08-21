from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from one_dragon.envs.download_service import DownloadService
from one_dragon.envs.env_config import EnvConfig
from one_dragon.envs.ghproxy_service import GhProxyService
from one_dragon.envs.git_service import GitService
from one_dragon.envs.launcher_service import LauncherService
from one_dragon.envs.mirrorchyan_config import MirrorChyanConfig
from one_dragon.envs.mirrorchyan_service import MirrorChyanService
from one_dragon.envs.project_config import ProjectConfig
from one_dragon.envs.python_service import PythonService
from one_dragon.utils import thread_utils

ONE_DRAGON_CONTEXT_EXECUTOR = ThreadPoolExecutor(thread_name_prefix='one_dragon_context', max_workers=1)


class OneDragonEnvContext:

    def __init__(self):
        """
        存项目和环境信息的
        安装器可以使用这个减少引入依赖
        """
        self.project_config: ProjectConfig = ProjectConfig()
        self.env_config: EnvConfig = EnvConfig()
        self.mirrorchyan_config: MirrorChyanConfig = MirrorChyanConfig()
        self.download_service: DownloadService = DownloadService(self.project_config, self.env_config)
        self.git_service: GitService = GitService(self.project_config, self.env_config, self.download_service)
        self.python_service: PythonService = PythonService(self.project_config, self.env_config, self.download_service)
        self.mirrorchyan_service: MirrorChyanService = MirrorChyanService(self.project_config, self.env_config, self.mirrorchyan_config)
        self.gh_proxy_service: GhProxyService = GhProxyService(self.env_config)
        self.installer_dir: Optional[str] = None
        self.launcher_service: LauncherService = LauncherService(self.project_config, self.env_config, self.download_service, self.mirrorchyan_service, self.git_service)

    def init_by_config(self) -> None:
        pass

    def async_update_gh_proxy(self) -> None:
        """
        异步更新gh proxy
        :return:
        """
        future = ONE_DRAGON_CONTEXT_EXECUTOR.submit(self.gh_proxy_service.update_proxy_url)
        future.add_done_callback(thread_utils.handle_future_result)

    def after_app_shutdown(self) -> None:
        """
        App关闭后进行的操作 关闭一切可能资源操作
        @return:
        """
        ONE_DRAGON_CONTEXT_EXECUTOR.shutdown(wait=False, cancel_futures=True)
