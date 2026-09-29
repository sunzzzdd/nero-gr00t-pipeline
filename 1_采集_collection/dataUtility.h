#pragma once
#ifndef _DATA_UTILITY_H_
#define _DATA_UTILITY_H_
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/header.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <deque>
#include <opencv2/imgproc.hpp>
#include <opencv2/opencv.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <data_msgs/msg/array.hpp>
#include <std_msgs/msg/string.hpp>
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <geometry_msgs/msg/twist_stamped.hpp>

class DataUtility: public rclcpp::Node
{
public:

    std::vector<std::string> cameraColorNames;
    std::vector<std::string> cameraDepthNames;
    std::vector<std::string> cameraPointCloudNames;
    std::vector<std::string> armJointStateNames;
    std::vector<std::string> armEndPoseNames;
    std::vector<std::string> localizationPoseNames;
    std::vector<std::string> force6dimNames;
    std::vector<std::string> gripperEncoderNames;
    std::vector<std::string> imu9AxisNames;
    std::vector<std::string> arrayFloat32Names;
    std::vector<std::string> lidarPointCloudNames;
    std::vector<std::string> robotBaseOdometryNames;
    std::vector<std::string> robotBaseVelocityNames;
    std::vector<std::string> liftMotorNames;

    std::vector<std::string> cameraColorTopics;
    std::vector<std::string> cameraDepthTopics;
    std::vector<std::string> cameraPointCloudTopics;
    std::vector<std::string> armJointStateTopics;
    std::vector<std::string> armEndPoseTopics;
    std::vector<std::string> localizationPoseTopics;
    std::vector<std::string> force6dimTopics;
    std::vector<std::string> gripperEncoderTopics;
    std::vector<std::string> imu9AxisTopics;
    std::vector<std::string> arrayFloat32Topics;
    std::vector<std::string> lidarPointCloudTopics;
    std::vector<std::string> robotBaseOdometryTopics;
    std::vector<std::string> robotBaseVelocityTopics;
    std::vector<std::string> liftMotorTopics;
    std::vector<std::string> instructionTextTopics;

    std::vector<std::string> cameraColorConfigTopics;
    std::vector<std::string> cameraDepthConfigTopics;
    std::vector<std::string> cameraPointCloudConfigTopics;
    std::vector<std::string> armJointStateConfigTopics;
    std::vector<std::string> armEndPoseConfigTopics;
    std::vector<std::string> localizationPoseConfigTopics;
    std::vector<std::string> force6dimConfigTopics;
    std::vector<std::string> gripperEncoderConfigTopics;
    std::vector<std::string> imu9AxisConfigTopics;
    std::vector<std::string> arrayFloat32ConfigTopics;
    std::vector<std::string> lidarPointCloudConfigTopics;
    std::vector<std::string> robotBaseOdometryConfigTopics;
    std::vector<std::string> robotBaseVelocityConfigTopics;
    std::vector<std::string> liftMotorConfigTopics;

    std::vector<std::string> cameraColorPublishTopics;
    std::vector<std::string> cameraDepthPublishTopics;
    std::vector<std::string> cameraPointCloudPublishTopics;
    std::vector<std::string> armJointStatePublishTopics;
    std::vector<std::string> armEndPosePublishTopics;
    std::vector<std::string> localizationPosePublishTopics;
    std::vector<std::string> force6dimPublishTopics;
    std::vector<std::string> gripperEncoderPublishTopics;
    std::vector<std::string> imu9AxisPublishTopics;
    std::vector<std::string> arrayFloat32PublishTopics;
    std::vector<std::string> lidarPointCloudPublishTopics;
    std::vector<std::string> robotBaseOdometryPublishTopics;
    std::vector<std::string> robotBaseVelocityPublishTopics;
    std::vector<std::string> liftMotorPublishTopics;

    std::vector<std::string> cameraColorConfigPublishTopics;
    std::vector<std::string> cameraDepthConfigPublishTopics;
    std::vector<std::string> cameraPointCloudConfigPublishTopics;
    std::vector<std::string> armJointStateConfigPublishTopics;
    std::vector<std::string> armEndPoseConfigPublishTopics;
    std::vector<std::string> localizationPoseConfigPublishTopics;
    std::vector<std::string> force6dimConfigPublishTopics;
    std::vector<std::string> gripperEncoderConfigPublishTopics;
    std::vector<std::string> imu9AxisConfigPublishTopics;
    std::vector<std::string> arrayFloat32ConfigPublishTopics;
    std::vector<std::string> lidarPointCloudConfigPublishTopics;
    std::vector<std::string> robotBaseOdometryConfigPublishTopics;
    std::vector<std::string> robotBaseVelocityConfigPublishTopics;
    std::vector<std::string> liftMotorConfigPublishTopics;

    std::vector<std::string> cameraColorParentFrames;
    std::vector<std::string> cameraDepthParentFrames;
    std::vector<std::string> cameraPointCloudParentFrames;
    std::vector<std::string> armJointStateParentFrames;
    std::vector<std::string> armEndPoseParentFrames;
    std::vector<std::string> localizationPoseParentFrames;
    std::vector<std::string> force6dimParentFrames;
    std::vector<std::string> gripperEncoderParentFrames;
    std::vector<std::string> imu9AxisParentFrames;
    std::vector<std::string> arrayFloat32ParentFrames;
    std::vector<std::string> lidarPointCloudParentFrames;
    std::vector<std::string> robotBaseOdometryParentFrames;
    std::vector<std::string> robotBaseVelocityParentFrames;
    std::vector<std::string> liftMotorParentFrames;

    std::vector<std::string> tfTransformParentFrames;
    std::vector<std::string> tfTransformChildFrames;

    std::vector<std::string> cameraColorDirs;
    std::vector<std::string> cameraDepthDirs;
    std::vector<std::string> cameraPointCloudDirs;
    std::vector<std::string> armJointStateDirs;
    std::vector<std::string> armEndPoseDirs;
    std::vector<std::string> localizationPoseDirs;
    std::vector<std::string> force6dimDirs;
    std::vector<std::string> gripperEncoderDirs;
    std::vector<std::string> imu9AxisDirs;
    std::vector<std::string> arrayFloat32Dirs;
    std::vector<std::string> lidarPointCloudDirs;
    std::vector<std::string> robotBaseOdometryDirs;
    std::vector<std::string> robotBaseVelocityDirs;
    std::vector<std::string> liftMotorDirs;
    std::vector<std::string> tfTransformDirs;
    std::string instructionsDir;
    std::string statisticsDir;

    std::vector<bool> cameraColorToSyncs;
    std::vector<bool> cameraDepthToSyncs;
    std::vector<bool> cameraPointCloudToSyncs;
    std::vector<bool> armJointStateToSyncs;
    std::vector<bool> armEndPoseToSyncs;
    std::vector<bool> localizationPoseToSyncs;
    std::vector<bool> force6dimToSyncs;
    std::vector<bool> gripperEncoderToSyncs;
    std::vector<bool> imu9AxisToSyncs;
    std::vector<bool> arrayFloat32ToSyncs;
    std::vector<bool> lidarPointCloudToSyncs;
    std::vector<bool> robotBaseOdometryToSyncs;
    std::vector<bool> robotBaseVelocityToSyncs;
    std::vector<bool> liftMotorToSyncs;

    std::vector<bool> cameraColorToPublishs;
    std::vector<bool> cameraDepthToPublishs;
    std::vector<bool> cameraPointCloudToPublishs;
    std::vector<bool> armJointStateToPublishs;
    std::vector<bool> armEndPoseToPublishs;
    std::vector<bool> localizationPoseToPublishs;
    std::vector<bool> force6dimToPublishs;
    std::vector<bool> gripperEncoderToPublishs;
    std::vector<bool> imu9AxisToPublishs;
    std::vector<bool> arrayFloat32ToPublishs;
    std::vector<bool> lidarPointCloudToPublishs;
    std::vector<bool> robotBaseOdometryToPublishs;
    std::vector<bool> robotBaseVelocityToPublishs;
    std::vector<bool> liftMotorToPublishs;
    std::vector<bool> tfTransformToPublishs;

    std::vector<double> cameraPointCloudMaxDistances;
    std::vector<double> cameraPointCloudDownSizes;

    std::vector<double> lidarPointCloudXDistanceUppers;
    std::vector<double> lidarPointCloudXDistancelowers;
    std::vector<double> lidarPointCloudYDistanceUppers;
    std::vector<double> lidarPointCloudYDistancelowers;
    std::vector<double> lidarPointCloudZDistanceUppers;
    std::vector<double> lidarPointCloudZDistancelowers;
    std::vector<double> lidarPointCloudDownSizes;

    std::vector<bool> armEndPoseOrients;

    float publishRate;
    int captureFrameNum;

    std::string datasetDir;
    int episodeIndex;

    std::string episodeDir;

    std::string cameraDir;
    std::string armDir;
    std::string localizationDir;
    std::string forceDir;
    std::string gripperDir;
    std::string imuDir;
    std::string arrayDir;
    std::string lidarDir;
    std::string robotBaseDir;
    std::string liftDir;
    std::string tfDir;

    std::string cameraColorDir;
    std::string cameraDepthDir;
    std::string cameraPointCloudDir;

    std::string armJointStateDir;
    std::string armEndPoseDir;

    std::string localizationPoseDir;

    std::string force6dimDir;

    std::string gripperEncoderDir;

    std::string imu9AxisDir;

    std::string arrayFloat32Dir;

    std::string lidarPointCloudDir;

    std::string robotBaseOdometryDir;

    std::string robotBaseVelocityDir;

    std::string liftMotorDir;

    std::string tfTransformDir;

    DataUtility(std::string name, const rclcpp::NodeOptions & options, std::string datasetDirParam, int episodeIndexParam): rclcpp::Node(name, options) 
    {
        declare_parameter("dataInfo.camera.color.names", std::vector<std::string>());get_parameter("dataInfo.camera.color.names", cameraColorNames);
        declare_parameter("dataInfo.camera.depth.names", std::vector<std::string>());get_parameter("dataInfo.camera.depth.names", cameraDepthNames);
        declare_parameter("dataInfo.camera.pointCloud.names", std::vector<std::string>());get_parameter("dataInfo.camera.pointCloud.names", cameraPointCloudNames);
        declare_parameter("dataInfo.arm.jointState.names", std::vector<std::string>());get_parameter("dataInfo.arm.jointState.names", armJointStateNames);
        declare_parameter("dataInfo.arm.endPose.names", std::vector<std::string>());get_parameter("dataInfo.arm.endPose.names", armEndPoseNames);
        declare_parameter("dataInfo.localization.pose.names", std::vector<std::string>());get_parameter("dataInfo.localization.pose.names", localizationPoseNames);
        declare_parameter("dataInfo.force.6dim.names", std::vector<std::string>());get_parameter("dataInfo.force.6dim.names", force6dimNames);
        declare_parameter("dataInfo.gripper.encoder.names", std::vector<std::string>());get_parameter("dataInfo.gripper.encoder.names", gripperEncoderNames);
        declare_parameter("dataInfo.imu.9axis.names", std::vector<std::string>());get_parameter("dataInfo.imu.9axis.names", imu9AxisNames);
        declare_parameter("dataInfo.array.float32.names", std::vector<std::string>());get_parameter("dataInfo.array.float32.names", arrayFloat32Names);
        declare_parameter("dataInfo.lidar.pointCloud.names", std::vector<std::string>());get_parameter("dataInfo.lidar.pointCloud.names", lidarPointCloudNames);
        declare_parameter("dataInfo.robotBase.odometry.names", std::vector<std::string>());get_parameter("dataInfo.robotBase.odometry.names", robotBaseOdometryNames);
        declare_parameter("dataInfo.robotBase.velocity.names", std::vector<std::string>());get_parameter("dataInfo.robotBase.velocity.names", robotBaseVelocityNames);
        declare_parameter("dataInfo.lift.motor.names", std::vector<std::string>());get_parameter("dataInfo.lift.motor.names", liftMotorNames);

        declare_parameter("dataInfo.camera.color.parentFrames", std::vector<std::string>());get_parameter("dataInfo.camera.color.parentFrames", cameraColorParentFrames);
        declare_parameter("dataInfo.camera.depth.parentFrames", std::vector<std::string>());get_parameter("dataInfo.camera.depth.parentFrames", cameraDepthParentFrames);
        declare_parameter("dataInfo.camera.pointCloud.parentFrames", std::vector<std::string>());get_parameter("dataInfo.camera.pointCloud.parentFrames", cameraPointCloudParentFrames);
        declare_parameter("dataInfo.arm.jointState.parentFrames", std::vector<std::string>());get_parameter("dataInfo.arm.jointState.parentFrames", armJointStateParentFrames);
        declare_parameter("dataInfo.arm.endPose.parentFrames", std::vector<std::string>());get_parameter("dataInfo.arm.endPose.parentFrames", armEndPoseParentFrames);
        declare_parameter("dataInfo.localization.pose.parentFrames", std::vector<std::string>());get_parameter("dataInfo.localization.pose.parentFrames", localizationPoseParentFrames);
        declare_parameter("dataInfo.force.6dim.parentFrames", std::vector<std::string>());get_parameter("dataInfo.force.6dim.parentFrames", force6dimParentFrames);
        declare_parameter("dataInfo.gripper.encoder.parentFrames", std::vector<std::string>());get_parameter("dataInfo.gripper.encoder.parentFrames", gripperEncoderParentFrames);
        declare_parameter("dataInfo.imu.9axis.parentFrames", std::vector<std::string>());get_parameter("dataInfo.imu.9axis.parentFrames", imu9AxisParentFrames);
        declare_parameter("dataInfo.array.float32.parentFrames", std::vector<std::string>());get_parameter("dataInfo.array.float32.parentFrames", arrayFloat32ParentFrames);
        declare_parameter("dataInfo.lidar.pointCloud.parentFrames", std::vector<std::string>());get_parameter("dataInfo.lidar.pointCloud.parentFrames", lidarPointCloudParentFrames);
        declare_parameter("dataInfo.robotBase.odometry.parentFrames", std::vector<std::string>());get_parameter("dataInfo.robotBase.odometry.parentFrames", robotBaseOdometryParentFrames);
        declare_parameter("dataInfo.robotBase.velocity.parentFrames", std::vector<std::string>());get_parameter("dataInfo.robotBase.velocity.parentFrames", robotBaseVelocityParentFrames);
        declare_parameter("dataInfo.lift.motor.parentFrames", std::vector<std::string>());get_parameter("dataInfo.lift.motor.parentFrames", liftMotorParentFrames);

        declare_parameter("dataInfo.tf.transform.parentFrames", std::vector<std::string>());get_parameter("dataInfo.tf.transform.parentFrames", tfTransformParentFrames);
        declare_parameter("dataInfo.tf.transform.childFrames", std::vector<std::string>());get_parameter("dataInfo.tf.transform.childFrames", tfTransformChildFrames);

        declare_parameter("dataInfo.camera.color.topics", std::vector<std::string>());get_parameter("dataInfo.camera.color.topics", cameraColorTopics);
        declare_parameter("dataInfo.camera.depth.topics", std::vector<std::string>());get_parameter("dataInfo.camera.depth.topics", cameraDepthTopics);
        declare_parameter("dataInfo.camera.pointCloud.topics", std::vector<std::string>());get_parameter("dataInfo.camera.pointCloud.topics", cameraPointCloudTopics);
        declare_parameter("dataInfo.arm.jointState.topics", std::vector<std::string>());get_parameter("dataInfo.arm.jointState.topics", armJointStateTopics);
        declare_parameter("dataInfo.arm.endPose.topics", std::vector<std::string>());get_parameter("dataInfo.arm.endPose.topics", armEndPoseTopics);
        declare_parameter("dataInfo.localization.pose.topics", std::vector<std::string>());get_parameter("dataInfo.localization.pose.topics", localizationPoseTopics);
        declare_parameter("dataInfo.force.6dim.topics", std::vector<std::string>());get_parameter("dataInfo.force.6dim.topics", force6dimTopics);
        declare_parameter("dataInfo.gripper.encoder.topics", std::vector<std::string>());get_parameter("dataInfo.gripper.encoder.topics", gripperEncoderTopics);
        declare_parameter("dataInfo.imu.9axis.topics", std::vector<std::string>());get_parameter("dataInfo.imu.9axis.topics", imu9AxisTopics);
        declare_parameter("dataInfo.array.float32.topics", std::vector<std::string>());get_parameter("dataInfo.array.float32.topics", arrayFloat32Topics);
        declare_parameter("dataInfo.lidar.pointCloud.topics", std::vector<std::string>());get_parameter("dataInfo.lidar.pointCloud.topics", lidarPointCloudTopics);
        declare_parameter("dataInfo.robotBase.odometry.topics", std::vector<std::string>());get_parameter("dataInfo.robotBase.odometry.topics", robotBaseOdometryTopics);
        declare_parameter("dataInfo.robotBase.velocity.topics", std::vector<std::string>());get_parameter("dataInfo.robotBase.velocity.topics", robotBaseVelocityTopics);
        declare_parameter("dataInfo.lift.motor.topics", std::vector<std::string>());get_parameter("dataInfo.lift.motor.topics", liftMotorTopics);
        declare_parameter("dataInfo.instruction.text.topics", std::vector<std::string>());get_parameter("dataInfo.instruction.text.topics", instructionTextTopics);

        declare_parameter("dataInfo.camera.color.pubTopics", std::vector<std::string>());get_parameter("dataInfo.camera.color.pubTopics", cameraColorPublishTopics);
        declare_parameter("dataInfo.camera.depth.pubTopics", std::vector<std::string>());get_parameter("dataInfo.camera.depth.pubTopics", cameraDepthPublishTopics);
        declare_parameter("dataInfo.camera.pointCloud.pubTopics", std::vector<std::string>());get_parameter("dataInfo.camera.pointCloud.pubTopics", cameraPointCloudPublishTopics);
        declare_parameter("dataInfo.arm.jointState.pubTopics", std::vector<std::string>());get_parameter("dataInfo.arm.jointState.pubTopics", armJointStatePublishTopics);
        declare_parameter("dataInfo.arm.endPose.pubTopics", std::vector<std::string>());get_parameter("dataInfo.arm.endPose.pubTopics", armEndPosePublishTopics);
        declare_parameter("dataInfo.localization.pose.pubTopics", std::vector<std::string>());get_parameter("dataInfo.localization.pose.pubTopics", localizationPosePublishTopics);
        declare_parameter("dataInfo.force.6dim.pubTopics", std::vector<std::string>());get_parameter("dataInfo.force.6dim.pubTopics", force6dimPublishTopics);
        declare_parameter("dataInfo.gripper.encoder.pubTopics", std::vector<std::string>());get_parameter("dataInfo.gripper.encoder.pubTopics", gripperEncoderPublishTopics);
        declare_parameter("dataInfo.imu.9axis.pubTopics", std::vector<std::string>());get_parameter("dataInfo.imu.9axis.pubTopics", imu9AxisPublishTopics);
        declare_parameter("dataInfo.array.float32.pubTopics", std::vector<std::string>());get_parameter("dataInfo.array.float32.pubTopics", arrayFloat32PublishTopics);
        declare_parameter("dataInfo.lidar.pointCloud.pubTopics", std::vector<std::string>());get_parameter("dataInfo.lidar.pointCloud.pubTopics", lidarPointCloudPublishTopics);
        declare_parameter("dataInfo.robotBase.odometry.pubTopics", std::vector<std::string>());get_parameter("dataInfo.robotBase.odometry.pubTopics", robotBaseOdometryPublishTopics);
        declare_parameter("dataInfo.robotBase.velocity.pubTopics", std::vector<std::string>());get_parameter("dataInfo.robotBase.velocity.pubTopics", robotBaseVelocityPublishTopics);
        declare_parameter("dataInfo.lift.motor.pubTopics", std::vector<std::string>());get_parameter("dataInfo.lift.motor.pubTopics", liftMotorPublishTopics);
        cameraColorPublishTopics = cameraColorPublishTopics.size() == 0 ? cameraColorTopics :cameraColorPublishTopics;
        cameraDepthPublishTopics = cameraDepthPublishTopics.size() == 0 ? cameraDepthTopics :cameraDepthPublishTopics;
        cameraPointCloudPublishTopics = cameraPointCloudPublishTopics.size() == 0 ? cameraPointCloudTopics :cameraPointCloudPublishTopics;
        armJointStatePublishTopics = armJointStatePublishTopics.size() == 0 ? armJointStateTopics :armJointStatePublishTopics;
        armEndPosePublishTopics = armEndPosePublishTopics.size() == 0 ? armEndPoseTopics :armEndPosePublishTopics;
        localizationPosePublishTopics = localizationPosePublishTopics.size() == 0 ? localizationPoseTopics :localizationPosePublishTopics;
        force6dimPublishTopics = force6dimPublishTopics.size() == 0 ? force6dimTopics :force6dimPublishTopics;
        gripperEncoderPublishTopics = gripperEncoderPublishTopics.size() == 0 ? gripperEncoderTopics :gripperEncoderPublishTopics;
        imu9AxisPublishTopics = imu9AxisPublishTopics.size() == 0 ? imu9AxisTopics :imu9AxisPublishTopics;
        arrayFloat32PublishTopics = arrayFloat32PublishTopics.size() == 0 ? arrayFloat32Topics :arrayFloat32PublishTopics;
        lidarPointCloudPublishTopics = lidarPointCloudPublishTopics.size() == 0 ? lidarPointCloudTopics :lidarPointCloudPublishTopics;
        robotBaseOdometryPublishTopics = robotBaseOdometryPublishTopics.size() == 0 ? robotBaseOdometryTopics :robotBaseOdometryPublishTopics;
        robotBaseVelocityPublishTopics = robotBaseVelocityPublishTopics.size() == 0 ? robotBaseVelocityTopics :robotBaseVelocityPublishTopics;
        liftMotorPublishTopics = liftMotorPublishTopics.size() == 0 ? liftMotorTopics :liftMotorPublishTopics;

        declare_parameter("dataInfo.camera.color.configTopics", std::vector<std::string>());get_parameter("dataInfo.camera.color.configTopics", cameraColorConfigTopics);
        declare_parameter("dataInfo.camera.depth.configTopics", std::vector<std::string>());get_parameter("dataInfo.camera.depth.configTopics", cameraDepthConfigTopics);
        declare_parameter("dataInfo.camera.pointCloud.configTopics", std::vector<std::string>());get_parameter("dataInfo.camera.pointCloud.configTopics", cameraPointCloudConfigTopics);
        declare_parameter("dataInfo.arm.jointState.configTopics", std::vector<std::string>());get_parameter("dataInfo.arm.jointState.configTopics", armJointStateConfigTopics);
        declare_parameter("dataInfo.arm.endPose.configTopics", std::vector<std::string>());get_parameter("dataInfo.arm.endPose.configTopics", armEndPoseConfigTopics);
        declare_parameter("dataInfo.localization.pose.configTopics", std::vector<std::string>());get_parameter("dataInfo.localization.pose.configTopics", localizationPoseConfigTopics);
        declare_parameter("dataInfo.force.6dim.configTopics", std::vector<std::string>());get_parameter("dataInfo.force.6dim.configTopics", force6dimConfigTopics);
        declare_parameter("dataInfo.gripper.encoder.configTopics", std::vector<std::string>());get_parameter("dataInfo.gripper.encoder.configTopics", gripperEncoderConfigTopics);
        declare_parameter("dataInfo.imu.9axis.configTopics", std::vector<std::string>());get_parameter("dataInfo.imu.9axis.configTopics", imu9AxisConfigTopics);
        declare_parameter("dataInfo.array.float32.configTopics", std::vector<std::string>());get_parameter("dataInfo.array.float32.configTopics", arrayFloat32ConfigTopics);
        declare_parameter("dataInfo.lidar.pointCloud.configTopics", std::vector<std::string>());get_parameter("dataInfo.lidar.pointCloud.configTopics", lidarPointCloudConfigTopics);
        declare_parameter("dataInfo.robotBase.odometry.configTopics", std::vector<std::string>());get_parameter("dataInfo.robotBase.odometry.configTopics", robotBaseOdometryConfigTopics);
        declare_parameter("dataInfo.robotBase.velocity.configTopics", std::vector<std::string>());get_parameter("dataInfo.robotBase.velocity.configTopics", robotBaseVelocityConfigTopics);
        declare_parameter("dataInfo.lift.motor.configTopics", std::vector<std::string>());get_parameter("dataInfo.lift.motor.configTopics", liftMotorConfigTopics);

        declare_parameter("dataInfo.camera.color.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.camera.color.pubConfigTopics", cameraColorConfigPublishTopics);
        declare_parameter("dataInfo.camera.depth.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.camera.depth.pubConfigTopics", cameraDepthConfigPublishTopics);
        declare_parameter("dataInfo.camera.pointCloud.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.camera.pointCloud.pubConfigTopics", cameraPointCloudConfigPublishTopics);
        declare_parameter("dataInfo.arm.jointState.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.arm.jointState.pubConfigTopics", armJointStateConfigPublishTopics);
        declare_parameter("dataInfo.arm.endPose.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.arm.endPose.pubConfigTopics", armEndPoseConfigPublishTopics);
        declare_parameter("dataInfo.localization.pose.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.localization.pose.pubConfigTopics", localizationPoseConfigPublishTopics);
        declare_parameter("dataInfo.force.6dim.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.force.6dim.pubConfigTopics", force6dimConfigPublishTopics);
        declare_parameter("dataInfo.gripper.encoder.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.gripper.encoder.pubConfigTopics", gripperEncoderConfigPublishTopics);
        declare_parameter("dataInfo.imu.9axis.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.imu.9axis.pubConfigTopics", imu9AxisConfigPublishTopics);
        declare_parameter("dataInfo.array.float32.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.array.float32.pubConfigTopics", arrayFloat32ConfigPublishTopics);
        declare_parameter("dataInfo.lidar.pointCloud.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.lidar.pointCloud.pubConfigTopics", lidarPointCloudConfigPublishTopics);
        declare_parameter("dataInfo.robotBase.odometry.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.robotBase.odometry.pubConfigTopics", robotBaseOdometryConfigPublishTopics);
        declare_parameter("dataInfo.robotBase.velocity.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.robotBase.velocity.pubConfigTopics", robotBaseVelocityConfigPublishTopics);
        declare_parameter("dataInfo.lift.motor.pubConfigTopics", std::vector<std::string>());get_parameter("dataInfo.lift.motor.pubConfigTopics", liftMotorConfigPublishTopics);
        cameraColorConfigPublishTopics = cameraColorConfigPublishTopics.size() == 0 ? cameraColorConfigTopics :cameraColorConfigPublishTopics;
        cameraDepthConfigPublishTopics = cameraDepthConfigPublishTopics.size() == 0 ? cameraDepthConfigTopics :cameraDepthConfigPublishTopics;
        cameraPointCloudConfigPublishTopics = cameraPointCloudConfigPublishTopics.size() == 0 ? cameraPointCloudConfigTopics :cameraPointCloudConfigPublishTopics;
        armJointStateConfigPublishTopics = armJointStateConfigPublishTopics.size() == 0 ? armJointStateConfigTopics :armJointStateConfigPublishTopics;
        armEndPoseConfigPublishTopics = armEndPoseConfigPublishTopics.size() == 0 ? armEndPoseConfigTopics :armEndPoseConfigPublishTopics;
        localizationPoseConfigPublishTopics = localizationPoseConfigPublishTopics.size() == 0 ? localizationPoseConfigTopics :localizationPoseConfigPublishTopics;
        force6dimConfigPublishTopics = force6dimConfigPublishTopics.size() == 0 ? force6dimConfigTopics :force6dimConfigPublishTopics;
        gripperEncoderConfigPublishTopics = gripperEncoderConfigPublishTopics.size() == 0 ? gripperEncoderConfigTopics :gripperEncoderConfigPublishTopics;
        imu9AxisConfigPublishTopics = imu9AxisConfigPublishTopics.size() == 0 ? imu9AxisConfigTopics :imu9AxisConfigPublishTopics;
        arrayFloat32ConfigPublishTopics = arrayFloat32ConfigPublishTopics.size() == 0 ? arrayFloat32ConfigTopics :arrayFloat32ConfigPublishTopics;
        lidarPointCloudConfigPublishTopics = lidarPointCloudConfigPublishTopics.size() == 0 ? lidarPointCloudConfigTopics :lidarPointCloudConfigPublishTopics;
        robotBaseOdometryConfigPublishTopics = robotBaseOdometryConfigPublishTopics.size() == 0 ? robotBaseOdometryConfigTopics :robotBaseOdometryConfigPublishTopics;
        robotBaseVelocityConfigPublishTopics = robotBaseVelocityConfigPublishTopics.size() == 0 ? robotBaseVelocityConfigTopics :robotBaseVelocityConfigPublishTopics;
        liftMotorConfigPublishTopics = liftMotorConfigPublishTopics.size() == 0 ? liftMotorConfigTopics :liftMotorConfigPublishTopics;

        declare_parameter("dataInfo.camera.color.toSyncs", std::vector<bool>());get_parameter("dataInfo.camera.color.toSyncs", cameraColorToSyncs);
        declare_parameter("dataInfo.camera.depth.toSyncs", std::vector<bool>());get_parameter("dataInfo.camera.depth.toSyncs", cameraDepthToSyncs);
        declare_parameter("dataInfo.camera.pointCloud.toSyncs", std::vector<bool>());get_parameter("dataInfo.camera.pointCloud.toSyncs", cameraPointCloudToSyncs);
        declare_parameter("dataInfo.arm.jointState.toSyncs", std::vector<bool>());get_parameter("dataInfo.arm.jointState.toSyncs", armJointStateToSyncs);
        declare_parameter("dataInfo.arm.endPose.toSyncs", std::vector<bool>());get_parameter("dataInfo.arm.endPose.toSyncs", armEndPoseToSyncs);
        declare_parameter("dataInfo.localization.pose.toSyncs", std::vector<bool>());get_parameter("dataInfo.localization.pose.toSyncs", localizationPoseToSyncs);
        declare_parameter("dataInfo.force.6dim.toSyncs", std::vector<bool>());get_parameter("dataInfo.force.6dim.toSyncs", force6dimToSyncs);
        declare_parameter("dataInfo.gripper.encoder.toSyncs", std::vector<bool>());get_parameter("dataInfo.gripper.encoder.toSyncs", gripperEncoderToSyncs);
        declare_parameter("dataInfo.imu.9axis.toSyncs", std::vector<bool>());get_parameter("dataInfo.imu.9axis.toSyncs", imu9AxisToSyncs);
        declare_parameter("dataInfo.array.float32.toSyncs", std::vector<bool>());get_parameter("dataInfo.array.float32.toSyncs", arrayFloat32ToSyncs);
        declare_parameter("dataInfo.lidar.pointCloud.toSyncs", std::vector<bool>());get_parameter("dataInfo.lidar.pointCloud.toSyncs", lidarPointCloudToSyncs);
        declare_parameter("dataInfo.robotBase.odometry.toSyncs", std::vector<bool>());get_parameter("dataInfo.robotBase.odometry.toSyncs", robotBaseOdometryToSyncs);
        declare_parameter("dataInfo.robotBase.velocity.toSyncs", std::vector<bool>());get_parameter("dataInfo.robotBase.velocity.toSyncs", robotBaseVelocityToSyncs);
        declare_parameter("dataInfo.lift.motor.toSyncs", std::vector<bool>());get_parameter("dataInfo.lift.motor.toSyncs", liftMotorToSyncs);
        cameraColorToSyncs = cameraColorToSyncs.size() == 0 ? std::vector<bool>(cameraColorTopics.size(), true) : cameraColorToSyncs;
        cameraDepthToSyncs = cameraDepthToSyncs.size() == 0 ? std::vector<bool>(cameraDepthTopics.size(), true) : cameraDepthToSyncs;
        cameraPointCloudToSyncs = cameraPointCloudToSyncs.size() == 0 ? std::vector<bool>(cameraPointCloudTopics.size(), true) : cameraPointCloudToSyncs;
        armJointStateToSyncs = armJointStateToSyncs.size() == 0 ? std::vector<bool>(armJointStateTopics.size(), true) : armJointStateToSyncs;
        armEndPoseToSyncs = armEndPoseToSyncs.size() == 0 ? std::vector<bool>(armEndPoseTopics.size(), true) : armEndPoseToSyncs;
        localizationPoseToSyncs = localizationPoseToSyncs.size() == 0 ? std::vector<bool>(localizationPoseTopics.size(), true) : localizationPoseToSyncs;
        force6dimToSyncs = force6dimToSyncs.size() == 0 ? std::vector<bool>(force6dimTopics.size(), true) : force6dimToSyncs;
        gripperEncoderToSyncs = gripperEncoderToSyncs.size() == 0 ? std::vector<bool>(gripperEncoderTopics.size(), true) : gripperEncoderToSyncs;
        imu9AxisToSyncs = imu9AxisToSyncs.size() == 0 ? std::vector<bool>(imu9AxisTopics.size(), true) : imu9AxisToSyncs;
        arrayFloat32ToSyncs = arrayFloat32ToSyncs.size() == 0 ? std::vector<bool>(arrayFloat32Topics.size(), true) : arrayFloat32ToSyncs;
        lidarPointCloudToSyncs = lidarPointCloudToSyncs.size() == 0 ? std::vector<bool>(lidarPointCloudTopics.size(), true) : lidarPointCloudToSyncs;
        robotBaseOdometryToSyncs = robotBaseOdometryToSyncs.size() == 0 ? std::vector<bool>(robotBaseOdometryTopics.size(), true) : robotBaseOdometryToSyncs;
        robotBaseVelocityToSyncs = robotBaseVelocityToSyncs.size() == 0 ? std::vector<bool>(robotBaseVelocityTopics.size(), true) : robotBaseVelocityToSyncs;
        liftMotorToSyncs = liftMotorToSyncs.size() == 0 ? std::vector<bool>(liftMotorTopics.size(), true) : liftMotorToSyncs;

        declare_parameter("dataInfo.camera.color.toPublishs", std::vector<bool>());get_parameter("dataInfo.camera.color.toPublishs", cameraColorToPublishs);
        declare_parameter("dataInfo.camera.depth.toPublishs", std::vector<bool>());get_parameter("dataInfo.camera.depth.toPublishs", cameraDepthToPublishs);
        declare_parameter("dataInfo.camera.pointCloud.toPublishs", std::vector<bool>());get_parameter("dataInfo.camera.pointCloud.toPublishs", cameraPointCloudToPublishs);
        declare_parameter("dataInfo.arm.jointState.toPublishs", std::vector<bool>());get_parameter("dataInfo.arm.jointState.toPublishs", armJointStateToPublishs);
        declare_parameter("dataInfo.arm.endPose.toPublishs", std::vector<bool>());get_parameter("dataInfo.arm.endPose.toPublishs", armEndPoseToPublishs);
        declare_parameter("dataInfo.localization.pose.toPublishs", std::vector<bool>());get_parameter("dataInfo.localization.pose.toPublishs", localizationPoseToPublishs);
        declare_parameter("dataInfo.force.6dim.toPublishs", std::vector<bool>());get_parameter("dataInfo.force.6dim.toPublishs", force6dimToPublishs);
        declare_parameter("dataInfo.gripper.encoder.toPublishs", std::vector<bool>());get_parameter("dataInfo.gripper.encoder.toPublishs", gripperEncoderToPublishs);
        declare_parameter("dataInfo.imu.9axis.toPublishs", std::vector<bool>());get_parameter("dataInfo.imu.9axis.toPublishs", imu9AxisToPublishs);
        declare_parameter("dataInfo.array.float32.toPublishs", std::vector<bool>());get_parameter("dataInfo.array.float32.toPublishs", arrayFloat32ToPublishs);
        declare_parameter("dataInfo.lidar.pointCloud.toPublishs", std::vector<bool>());get_parameter("dataInfo.lidar.pointCloud.toPublishs", lidarPointCloudToPublishs);
        declare_parameter("dataInfo.robotBase.odometry.toPublishs", std::vector<bool>());get_parameter("dataInfo.robotBase.odometry.toPublishs", robotBaseOdometryToPublishs);
        declare_parameter("dataInfo.robotBase.velocity.toPublishs", std::vector<bool>());get_parameter("dataInfo.robotBase.velocity.toPublishs", robotBaseVelocityToPublishs);
        declare_parameter("dataInfo.lift.motor.toPublishs", std::vector<bool>());get_parameter("dataInfo.lift.motor.toPublishs", liftMotorToPublishs);
        declare_parameter("dataInfo.tf.transform.toPublishs", std::vector<bool>());get_parameter("dataInfo.tf.transform.toPublishs", tfTransformToPublishs);
        cameraColorToPublishs = cameraColorToPublishs.size() == 0 ? std::vector<bool>(cameraColorTopics.size(), true) : cameraColorToPublishs;
        cameraDepthToPublishs = cameraDepthToPublishs.size() == 0 ? std::vector<bool>(cameraDepthTopics.size(), true) : cameraDepthToPublishs;
        cameraPointCloudToPublishs = cameraPointCloudToPublishs.size() == 0 ? std::vector<bool>(cameraPointCloudTopics.size(), true) : cameraPointCloudToPublishs;
        armJointStateToPublishs = armJointStateToPublishs.size() == 0 ? std::vector<bool>(armJointStateTopics.size(), true) : armJointStateToPublishs;
        armEndPoseToPublishs = armEndPoseToPublishs.size() == 0 ? std::vector<bool>(armEndPoseTopics.size(), true) : armEndPoseToPublishs;
        localizationPoseToPublishs = localizationPoseToPublishs.size() == 0 ? std::vector<bool>(localizationPoseTopics.size(), true) : localizationPoseToPublishs;
        force6dimToPublishs = force6dimToPublishs.size() == 0 ? std::vector<bool>(force6dimTopics.size(), true) : force6dimToPublishs;
        gripperEncoderToPublishs = gripperEncoderToPublishs.size() == 0 ? std::vector<bool>(gripperEncoderTopics.size(), true) : gripperEncoderToPublishs;
        imu9AxisToPublishs = imu9AxisToPublishs.size() == 0 ? std::vector<bool>(imu9AxisTopics.size(), true) : imu9AxisToPublishs;
        arrayFloat32ToPublishs = arrayFloat32ToPublishs.size() == 0 ? std::vector<bool>(arrayFloat32Topics.size(), true) : arrayFloat32ToPublishs;
        lidarPointCloudToPublishs = lidarPointCloudToPublishs.size() == 0 ? std::vector<bool>(lidarPointCloudTopics.size(), true) : lidarPointCloudToPublishs;
        robotBaseOdometryToPublishs = robotBaseOdometryToPublishs.size() == 0 ? std::vector<bool>(robotBaseOdometryTopics.size(), true) : robotBaseOdometryToPublishs;
        robotBaseVelocityToPublishs = robotBaseVelocityToPublishs.size() == 0 ? std::vector<bool>(robotBaseVelocityTopics.size(), true) : robotBaseVelocityToPublishs;
        liftMotorToPublishs = liftMotorToPublishs.size() == 0 ? std::vector<bool>(liftMotorTopics.size(), true) : liftMotorToPublishs;
        tfTransformToPublishs = tfTransformToPublishs.size() == 0 ? std::vector<bool>(tfTransformParentFrames.size(), true) : tfTransformToPublishs;

        declare_parameter("dataInfo.camera.pointCloud.maxDistances", std::vector<double>());get_parameter("dataInfo.camera.pointCloud.maxDistances", cameraPointCloudMaxDistances);
        declare_parameter("dataInfo.camera.pointCloud.downSizes", std::vector<double>());get_parameter("dataInfo.camera.pointCloud.downSizes", cameraPointCloudDownSizes);

        declare_parameter("dataInfo.lidar.pointCloud.xDistanceUppers", std::vector<double>());get_parameter("dataInfo.lidar.pointCloud.xDistanceUppers", lidarPointCloudXDistanceUppers);
        declare_parameter("dataInfo.lidar.pointCloud.xDistanceLowers", std::vector<double>());get_parameter("dataInfo.lidar.pointCloud.xDistanceLowers", lidarPointCloudXDistancelowers);
        declare_parameter("dataInfo.lidar.pointCloud.yDistanceUppers", std::vector<double>());get_parameter("dataInfo.lidar.pointCloud.yDistanceUppers", lidarPointCloudYDistanceUppers);
        declare_parameter("dataInfo.lidar.pointCloud.yDistanceLowers", std::vector<double>());get_parameter("dataInfo.lidar.pointCloud.yDistanceLowers", lidarPointCloudYDistancelowers);
        declare_parameter("dataInfo.lidar.pointCloud.zDistanceUppers", std::vector<double>());get_parameter("dataInfo.lidar.pointCloud.zDistanceUppers", lidarPointCloudZDistanceUppers);
        declare_parameter("dataInfo.lidar.pointCloud.zDistanceLowers", std::vector<double>());get_parameter("dataInfo.lidar.pointCloud.zDistanceLowers", lidarPointCloudZDistancelowers);
        declare_parameter("dataInfo.lidar.pointCloud.downSizes", std::vector<double>());get_parameter("dataInfo.lidar.pointCloud.downSizes", lidarPointCloudDownSizes);

        declare_parameter("dataInfo.arm.endPose.orients", std::vector<bool>());get_parameter("dataInfo.arm.endPose.orients", armEndPoseOrients);
        armEndPoseOrients = armEndPoseOrients.size() == 0 ? std::vector<bool>(armEndPoseNames.size(), true) : armEndPoseOrients;

        datasetDir = datasetDirParam;
        episodeIndex = episodeIndexParam;

        episodeDir = datasetDir + "/episode" + std::to_string(episodeIndex);
        // episodeDir = episodeDir.replace("//", "/");

        cameraDir = episodeDir + "/camera";
        armDir = episodeDir + "/arm";
        localizationDir = episodeDir + "/localization";
        forceDir = episodeDir + "/force";
        gripperDir = episodeDir + "/gripper";
        imuDir = episodeDir + "/imu";
        arrayDir = episodeDir + "/array";
        lidarDir = episodeDir + "/lidar";
        robotBaseDir = episodeDir + "/robotBase";
        liftDir = episodeDir + "/lift";
        tfDir = episodeDir + "/tf";

        cameraColorDir = cameraDir + "/color";
        cameraDepthDir = cameraDir + "/depth";
        cameraPointCloudDir = cameraDir + "/pointCloud";
        armJointStateDir = armDir + "/jointState";
        armEndPoseDir = armDir + "/endPose";
        localizationPoseDir = localizationDir + "/pose";
        force6dimDir = forceDir + "/6dim";
        gripperEncoderDir = gripperDir + "/encoder";
        imu9AxisDir = imuDir + "/9axis";
        arrayFloat32Dir = arrayDir + "/float32";
        lidarPointCloudDir = lidarDir + "/pointCloud";
        robotBaseOdometryDir = robotBaseDir + "/odometry";
        robotBaseVelocityDir = robotBaseDir + "/velocity";
        liftMotorDir = liftDir + "/motor";
        tfTransformDir = tfDir + "/transform";

        instructionsDir = episodeDir + "/instructions.json";
        statisticsDir = episodeDir + "/statistic.txt";

        for(int i = 0; i < cameraColorNames.size(); i++){
            std::string dir = cameraColorDir + "/" + cameraColorNames.at(i);
            cameraColorDirs.push_back(dir);
        }
        for(int i = 0; i < cameraDepthNames.size(); i++){
            std::string dir = cameraDepthDir + "/" + cameraDepthNames.at(i);
            cameraDepthDirs.push_back(dir);
        }
        for(int i = 0; i < cameraPointCloudNames.size(); i++){
            std::string dir = cameraPointCloudDir + "/" + cameraPointCloudNames.at(i);
            cameraPointCloudDirs.push_back(dir);
        }
        for(int i = 0; i < armJointStateNames.size(); i++){
            std::string dir = armJointStateDir + "/" + armJointStateNames.at(i);
            armJointStateDirs.push_back(dir);
        }
        for(int i = 0; i < armEndPoseNames.size(); i++){
            std::string dir = armEndPoseDir + "/" + armEndPoseNames.at(i);
            armEndPoseDirs.push_back(dir);
        }
        for(int i = 0; i < localizationPoseNames.size(); i++){
            std::string dir = localizationPoseDir + "/" + localizationPoseNames.at(i);
            localizationPoseDirs.push_back(dir);
        }
        for(int i = 0; i < force6dimNames.size(); i++){
            std::string dir = force6dimDir + "/" + force6dimNames.at(i);
            force6dimDirs.push_back(dir);
        }
        for(int i = 0; i < gripperEncoderNames.size(); i++){
            std::string dir = gripperEncoderDir + "/" + gripperEncoderNames.at(i);
            gripperEncoderDirs.push_back(dir);
        }
        for(int i = 0; i < imu9AxisNames.size(); i++){
            std::string dir = imu9AxisDir + "/" + imu9AxisNames.at(i);
            imu9AxisDirs.push_back(dir);
        }
        for(int i = 0; i < arrayFloat32Names.size(); i++){
            std::string dir = arrayFloat32Dir + "/" + arrayFloat32Names.at(i);
            arrayFloat32Dirs.push_back(dir);
        }
        for(int i = 0; i < lidarPointCloudNames.size(); i++){
            std::string dir = lidarPointCloudDir + "/" + lidarPointCloudNames.at(i);
            lidarPointCloudDirs.push_back(dir);
        }
        for(int i = 0; i < robotBaseOdometryNames.size(); i++){
            std::string dir = robotBaseOdometryDir + "/" + robotBaseOdometryNames.at(i);
            robotBaseOdometryDirs.push_back(dir);
        }
        for(int i = 0; i < robotBaseVelocityNames.size(); i++){
            std::string dir = robotBaseVelocityDir + "/" + robotBaseVelocityNames.at(i);
            robotBaseVelocityDirs.push_back(dir);
        }
        for(int i = 0; i < liftMotorNames.size(); i++){
            std::string dir = liftMotorDir + "/" + liftMotorNames.at(i);
            liftMotorDirs.push_back(dir);
        }
        for(int i = 0; i < tfTransformParentFrames.size(); i++){
            std::string dir = tfTransformDir + "/" + tfTransformParentFrames.at(i) + "-" + tfTransformChildFrames.at(i) + ".json";
            tfTransformDirs.push_back(dir);
        }
    }
};

#endif
