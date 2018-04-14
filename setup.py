# -*- coding: utf-8 -*-


from setuptools import setup, find_packages
import subprocess


# -----------------------------------------------------------------------------
def main():
    """main setup method"""
    setup(
        name="ouroboros-tools-pproject",
        version=subprocess.check_output(['git', 'describe', '--tag']).strip().decode('ascii').replace('-', '_'),
        packages=find_packages(),
        package_data={'ouroboros.tools.pproject': [
            'pproject_config.yml']},
        include_package_data=True,
        zip_safe=False)


# =============================================================================
if __name__ == '__main__':
    main()
