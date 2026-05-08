"""Install fvctools from CodeArtifact using uv."""

import os
import sys

from duct import cmd

CODEARTIFACT_HOST = 'flyvercity-368281077578.d.codeartifact.eu-west-3.amazonaws.com'

password = os.environ.get('UV_INDEX_CODEARTIFACT_PASSWORD')
if not password:
    print("Error: UV_INDEX_CODEARTIFACT_PASSWORD is not set.")
    print("Run the Login-ToCodeArtifact script first.")
    sys.exit(1)

index_url = f'https://aws:{password}@{CODEARTIFACT_HOST}/pypi/tools/simple/'

print('Installing fvctools from CodeArtifact...')

cmd(
    'uv', 'tool', 'install', 'fvctools',
    '--index', index_url,
    '--prerelease=allow',
    '--extra-index-url', 'https://pypi.org/simple',
).run()
