from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'ball_tracking_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='Kobuki QBot Blue Ball Tracking Package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # We now have two separate executable scripts
            'vision_node = ball_tracking_pkg.vision_node:main',
            'control_node = ball_tracking_pkg.control_node:main',
        ],
    },
)