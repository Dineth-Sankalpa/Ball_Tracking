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
        
        # This line tells ROS2 to install your launch files
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='dinethsankalpaofficial@gmail.com',
    description='Kobuki QBot Blue Ball Tracking via Xbox360 RGBD Camera',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # FORMAT: executable_name = package_name.python_script_name:main
            'tracker = ball_tracking_pkg.tracker:main',
        ],
    },
)