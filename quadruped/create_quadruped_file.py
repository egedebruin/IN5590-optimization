import os

def generate_quadruped_urdf(
    filename="generated_quadruped.urdf",
    torso_size=(0.6, 0.4, 0.1),  # Wider and deeper
    upper_leg_length=0.2,        # Shorter legs
    lower_leg_length=0.2,
    leg_width=0.06
):
    torso_width, torso_depth, torso_height = torso_size

    # Widen leg positions
    leg_positions = [
        (+torso_width/2, +torso_depth/2, 0),
        (+torso_width/2, -torso_depth/2, 0),
        (-torso_width/2, +torso_depth/2, 0),
        (-torso_width/2, -torso_depth/2, 0),
    ]

    urdf = f"""<?xml version="1.0" ?>
<robot name="generated_quadruped">

  <!-- Torso -->
  <link name="torso">
    <inertial>
      <mass value="5"/>
      <origin xyz="0 0 0"/>
      <inertia ixx="0.2" iyy="0.2" izz="0.2" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <geometry>
        <box size="{torso_width} {torso_depth} {torso_height}"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <box size="{torso_width} {torso_depth} {torso_height}"/>
      </geometry>
    </collision>
  </link>
"""

    for i, (x, y, z) in enumerate(leg_positions):
        upper = f"upper_leg_{i}"
        lower = f"lower_leg_{i}"
        hip = f"hip_{i}"
        knee = f"knee_{i}"

        urdf += f"""
  <!-- Leg {i} -->
  <link name="{upper}">
    <inertial>
      <mass value="1.5"/>
      <origin xyz="0 0 {-upper_leg_length / 2}"/>
      <inertia ixx="0.02" iyy="0.02" izz="0.02" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <origin xyz="0 0 {-upper_leg_length / 2}"/>
      <geometry>
        <box size="{leg_width} {leg_width} {upper_leg_length}"/>
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 {-upper_leg_length / 2}"/>
      <geometry>
        <box size="{leg_width} {leg_width} {upper_leg_length}"/>
      </geometry>
    </collision>
  </link>

  <link name="{lower}">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 {-lower_leg_length / 2}"/>
      <inertia ixx="0.01" iyy="0.01" izz="0.01" ixy="0" ixz="0" iyz="0"/>
    </inertial>
    <visual>
      <origin xyz="0 0 {-lower_leg_length / 2}"/>
      <geometry>
        <box size="{leg_width} {leg_width} {lower_leg_length}"/>
      </geometry>
    </visual>
    <collision>
      <origin xyz="0 0 {-lower_leg_length / 2}"/>
      <geometry>
        <box size="{leg_width} {leg_width} {lower_leg_length}"/>
      </geometry>
    </collision>
  </link>

  <!-- Hip joint -->
  <joint name="{hip}" type="revolute">
    <parent link="torso"/>
    <child link="{upper}"/>
    <origin xyz="{x} {y} {-torso_height / 2}" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <dynamics damping="0.5" friction="0.1"/>
    <limit effort="20" velocity="10" lower="-1.57" upper="1.57"/>
  </joint>

  <!-- Knee joint -->
  <joint name="{knee}" type="revolute">
    <parent link="{upper}"/>
    <child link="{lower}"/>
    <origin xyz="0 0 {-upper_leg_length}" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <dynamics damping="0.5" friction="0.1"/>
    <limit effort="20" velocity="10" lower="-1.57" upper="0"/>
  </joint>
"""

    urdf += "\n</robot>"

    with open(filename, "w") as f:
        f.write(urdf)

    print(f"✅ URDF written to {filename}")


if __name__ == "__main__":
    generate_quadruped_urdf(
        filename="files/generated_quadruped.urdf",
        torso_size=(0.6, 0.4, 0.1),
        upper_leg_length=0.2,
        lower_leg_length=0.2,
        leg_width=0.06
    )
