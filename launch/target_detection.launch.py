# Copyright (c) 2022，Horizon Robotics.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.substitutions import TextSubstitution
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python import get_package_share_directory


def generate_launch_description():
    # args that can be set from the command line or a default will be used
    image_width_launch_arg = DeclareLaunchArgument(
        "dnn_sample_image_width", default_value=TextSubstitution(text="640")
    )
    image_height_launch_arg = DeclareLaunchArgument(
        "dnn_sample_image_height", default_value=TextSubstitution(text="480")
    )

    web_show = os.getenv('WEB_SHOW')
    print("web_show is ", web_show)

    usb_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('hobot_usb_cam'),
                'launch/hobot_usb_cam.launch.py')),
        launch_arguments={
            'usb_image_width': '640',
            'usb_image_height': '480',
            'usb_pixel_format': 'yuyv2rgb',
            'usb_zero_copy': 'False',
            'usb_framerate': '5',
        }.items()
    )

    TonyPi_image_correct = Node(
        package='TonyPi_image_correct',
        executable='TonyPi_image_correct',
        parameters=[
            {"pub_image_topic": 'hb_image'},
        ],
        arguments=['--ros-args', '--log-level', 'warn']
    )


    jpeg_codec_node = Node(
        package='hobot_codec',
        executable='hobot_codec_republish',
        output='screen',
        parameters=[
            {"in_mode": 'shared_mem'},
            {"in_format": "nv12"},
            {"out_mode": 'ros'},
            {"out_format": "jpeg"},
            {"sub_topic": 'hb_image'},
            {"dump_output": False},
            {"pub_topic": 'image_jpeg'},
        ],
        arguments=['--ros-args', '--log-level', 'error']
    )


    web_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('websocket'),
                'launch/websocket.launch.py')),
        launch_arguments={
            'websocket_image_topic': '/image_jpeg',
            'websocket_smart_topic': '/robot_target_detection'
        }.items()
    )


    # 障碍物检测pkg
    TonyPi_target_detection_node = Node(
        package='TonyPi_target_detection',
        executable='TonyPi_target_detection',
        output='screen',
        parameters=[
            {"is_shared_mem_sub": True},
            {"sub_img_topic": "/hb_image"},
            {"config_file": "config/TonyPi_yolov5sconfig.json"},
        ],
        arguments=['--ros-args', '--log-level', 'error']
    )

    # return LaunchDescription([
    #     usb_node,
    #     robot_image_correct,
    #     jpeg_codec_node,
    #     nv12_codec_node,
    #     racing_obstacle_detection_yolov5_node
    # ])
    if web_show == "TRUE":
        return LaunchDescription([
            usb_node,
            TonyPi_image_correct,
            jpeg_codec_node,
            TonyPi_target_detection_node,
            web_node
        ])
    else:
        return LaunchDescription([
            usb_node,
            TonyPi_image_correct,
            TonyPi_target_detection_node
        ])