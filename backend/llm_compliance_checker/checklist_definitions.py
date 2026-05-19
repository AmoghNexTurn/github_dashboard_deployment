# llm_compliance_checker/checklist_definitions.py
"""
Checklist definitions for each directory type.
"""

CHECKLISTS = {
    'frontend': [
        {'name': 'has_package_json',
            'description': 'Has package.json or lockfile', 'severity': 'error'},
        {'name': 'has_src_folder', 'description': 'Has src/ folder',
            'severity': 'warning'},
        {'name': 'has_static_assets',
            'description': 'Has public/, assets/, or static/ folder', 'severity': 'info'},
        {'name': 'has_entry_file',
            'description': 'Has index.*, main.*, or App.* file', 'severity': 'warning'},
        {'name': 'has_build_config',
            'description': 'Has vite.config.*, webpack.config.*, or next.config.*', 'severity': 'info'},
        {'name': 'has_ui_folders',
            'description': 'Has components/, pages/, or views/ folder', 'severity': 'warning'},
        {'name': 'has_styles',
            'description': 'Has styles/ folder or CSS files', 'severity': 'info'},
        {'name': 'has_env_config', 'description': 'Has .env files', 'severity': 'info'}
    ],
    'backend': [
        {'name': 'has_dependency_file',
            'description': 'Has dependency file (package.json, requirements.txt, etc.)', 'severity': 'error'},
        {'name': 'has_api_dirs', 'description': 'Has routes/, controllers/, or api/ folder',
            'severity': 'warning'},
        {'name': 'has_models', 'description': 'Has models/, schemas/, or entities/ folder',
            'severity': 'warning'},
        {'name': 'has_config',
            'description': 'Has config/, settings/, or core/ folder', 'severity': 'info'},
        {'name': 'has_middleware_services',
            'description': 'Has middleware/ or services/ folder', 'severity': 'info'},
        {'name': 'has_entry_point',
            'description': 'Has app.*, main.*, or server.* file', 'severity': 'warning'},
        {'name': 'has_db_files',
            'description': 'Has migrations/, prisma/, or alembic/ folder', 'severity': 'info'},
        {'name': 'has_env_config', 'description': 'Has .env files', 'severity': 'info'}
    ],
    'infrastructure': [
        {'name': 'has_docker_files',
            'description': 'Has Dockerfile or docker-compose files', 'severity': 'error'},
        {'name': 'has_k8s_manifests',
            'description': 'Has .yaml/.yml files or k8s/ folder', 'severity': 'info'},
        {'name': 'has_proxy_config',
            'description': 'Has nginx/ or traefik/ config', 'severity': 'info'},
        {'name': 'has_iac', 'description': 'Has terraform/ or pulumi/ config',
            'severity': 'info'},
        {'name': 'has_cicd', 'description': 'Has .github/, .gitlab/, or CI config files',
            'severity': 'warning'},
        {'name': 'has_env_folders',
            'description': 'Has prod/, staging/, or dev/ folders', 'severity': 'info'},
        {'name': 'has_deploy_scripts',
            'description': 'Has scripts/ folder or deploy.* files', 'severity': 'warning'},
        {'name': 'has_monitoring',
            'description': 'Has prometheus/, grafana/, or monitoring/ config', 'severity': 'info'}
    ],
    'shared': [
        {'name': 'has_utils', 'description': 'Has utils/ or helpers/ folder',
            'severity': 'warning'},
        {'name': 'has_types', 'description': 'Has types/ or interfaces/ folder',
            'severity': 'info'},
        {'name': 'has_schemas',
            'description': 'Has schemas/ or validators/ folder', 'severity': 'info'},
        {'name': 'has_api_clients',
            'description': 'Has api/ or clients/ folder', 'severity': 'info'},
        {'name': 'has_constants',
            'description': 'Has constants/ or config/ folder', 'severity': 'info'},
        {'name': 'has_libs', 'description': 'Has packages/ or libs/ folder',
            'severity': 'info'},
        {'name': 'has_test_utils',
            'description': 'Has test-utils/ folder', 'severity': 'info'},
        {'name': 'has_readme', 'description': 'Has README.md', 'severity': 'warning'}
    ],
    'docs': [
        {'name': 'has_markdown', 'description': 'Has .md files', 'severity': 'error'},
        {'name': 'has_architecture_docs',
            'description': 'Has architecture/ folder or diagram files', 'severity': 'info'},
        {'name': 'has_examples',
            'description': 'Has examples/ or templates/ folder', 'severity': 'info'},
        {'name': 'has_scripts', 'description': 'Has scripts/ folder', 'severity': 'info'},
        {'name': 'has_tests', 'description': 'Has tests/, integration/, or e2e/ folder',
            'severity': 'warning'},
        {'name': 'has_contribution_docs',
            'description': 'Has CONTRIBUTING or CODE_OF_CONDUCT files', 'severity': 'info'},
        {'name': 'has_changelog',
            'description': 'Has CHANGELOG or HISTORY files', 'severity': 'info'},
        {'name': 'has_license', 'description': 'Has LICENSE file', 'severity': 'warning'}
    ]
}

CATEGORY_PATTERNS = {
    'frontend': [r'^frontend$', r'^client$', r'^web$', r'^ui$', r'^app$'],
    'backend': [r'^backend$', r'^server$', r'^api$', r'^services?$'],
    'infrastructure': [r'^infra(structure)?$', r'^docker$', r'^deployment$', r'^k8s$', r'^kubernetes$', r'^nginx$'],
    'shared': [r'^shared$', r'^common$', r'^lib$', r'^core$', r'^packages$'],
    'docs': [r'^docs?$', r'^scripts$', r'^tests?$', r'^examples?$']
}
