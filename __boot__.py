# custom_bootstrap.py
def _site_packages():
    import site
    import sys
    import os
    paths = []
    prefixes = [sys.prefix]
    if sys.exec_prefix != sys.prefix:
        prefixes.append(sys.exec_prefix)
    for prefix in prefixes:
        paths.append(os.path.join(prefix, 'lib', 'python' + sys.version[:3],
                                  'site-packages'))
    
    if os.path.join('.framework', '') in sys.prefix:
        home = os.environ.get('HOME')
        if home:
            paths.append(os.path.join(home, 'Library', 'Python',
                                     sys.version[:3], 'site-packages'))
    
    # Work around for numpy import issue
    for path in list(paths):
        site.addsitedir(path)
    
    return paths

# Fix numpy import
import sys
import os
import re

# Add the site-packages directory
_site_packages()

# Explicitly set numpy path if needed
numpy_path = None
for path in sys.path:
    if os.path.exists(os.path.join(path, 'numpy')):
        numpy_path = path
        break

if numpy_path:
    sys.path.insert(0, numpy_path)