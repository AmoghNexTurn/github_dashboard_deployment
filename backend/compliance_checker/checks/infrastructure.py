# checks/infrastructure.py
"""
Infrastructure directory checker.
"""

from typing import List, Dict, Any
from .base import BaseChecker


class InfrastructureChecker(BaseChecker):
    """Checker for infrastructure directories."""

    def get_checks(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'has_docker_files',
                'function': lambda: self._has_file_matching(['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']),
                'severity': 'error',
                'pass_message': 'Docker configuration found',
                'fail_message': 'No Dockerfile or docker-compose files found'
            },
            {
                'name': 'has_k8s_manifests',
                'function': lambda: self._has_file_matching(['.yaml', '.yml']) or self._has_dir_matching(['k8s', 'kubernetes']),
                'severity': 'info',
                'pass_message': 'Kubernetes manifests found',
                'fail_message': 'No K8s YAML files or k8s/ folder found'
            },
            {
                'name': 'has_proxy_config',
                'function': lambda: self._has_dir_matching(['nginx', 'traefik']) or self._has_file_matching(['nginx.conf']),
                'severity': 'info',
                'pass_message': 'Proxy configuration found',
                'fail_message': 'No nginx/traefik configs found'
            },
            {
                'name': 'has_iac',
                'function': lambda: self._has_dir_matching(['terraform', 'pulumi']) or self._has_file_matching(['.tf']),
                'severity': 'info',
                'pass_message': 'Infrastructure as Code found',
                'fail_message': 'No terraform/pulumi configs found'
            },
            {
                'name': 'has_cicd',
                'function': lambda: self._has_dir_matching(['.github', '.gitlab']) or self._has_file_matching(['.yml', '.yaml', 'Jenkinsfile']),
                'severity': 'warning',
                'pass_message': 'CI/CD configuration found',
                'fail_message': 'No CI/CD configs found'
            },
            {
                'name': 'has_env_folders',
                'function': lambda: self._has_dir_matching(['prod', 'staging', 'dev', 'production', 'development']),
                'severity': 'info',
                'pass_message': 'Environment-specific folders found',
                'fail_message': 'No environment folders (prod/staging/dev) found'
            },
            {
                'name': 'has_deploy_scripts',
                'function': lambda: self._has_dir_matching(['scripts']) or self._has_file_matching(['deploy.']),
                'severity': 'warning',
                'pass_message': 'Deployment scripts found',
                'fail_message': 'No scripts/ folder or deploy.* files found'
            },
            {
                'name': 'has_monitoring',
                'function': lambda: self._has_dir_matching(['prometheus', 'grafana', 'monitoring']),
                'severity': 'info',
                'pass_message': 'Monitoring configuration found',
                'fail_message': 'No monitoring configs found'
            }
        ]
