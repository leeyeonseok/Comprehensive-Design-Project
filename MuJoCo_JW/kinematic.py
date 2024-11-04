import mujoco_py
from functions import *
from scipy.linalg import expm
from math import pi

class Kinematic:
    def __init__(self, sim):
        self.sim = sim
        self.model = sim.model
        self.data = sim.data

    
    def get_first_wv(self):
        """
        실제 로봇의 w,v 를 넣으면 됨
        """
        w,q = [], []
        # Simulation
        # for i in range(self.model.nbody - 2): # except gripper
        #     w.append(self.data.xaxis[i])
        
        # for i in range(1, self.model.nbody - 1):
        #     q.append(self.data.body_xpos[i])
        
        #==================4DOF========================
        # w = np.array([[0, 0, 1],
        #               [0,-1, 0],
        #               [0,-1, 0],
        #               [0,-1, 0]])
        
        # q = np.array([np.array([0, 0, 0]).T,
        #               np.array([0, 0, 0.5]).T,
        #               np.array([0, 0, 0.5]).T + Rot_y(10) @ np.array([0, 0, 0.8]).T,
        #               np.array([0, 0, 0.5]).T + Rot_y(10) @ np.array([0, 0, 0.8]).T + Rot_y(10) @ Rot_y(10) @ np.array([0, 0, 1.0]).T])

        #==================Open4DOF========================
        w = np.array([[0, 0, 1],
                      [0,-1, 0],
                      [0,-1, 0],
                      [0,-1, 0]])
        
        q = np.array([np.array([0, 0, 0]).T,
                      np.array([0, 0, 0.3825]).T,
                      np.array([0, 0, 0.3825]).T + Rot_x(90) @ Rot_z(90) @ np.array([0.12, 0.64, 0]).T,
                      np.array([0, 0, 0.3825]).T + Rot_x(90) @ Rot_z(90) @ np.array([0.12, 0.64, 0]).T + Rot_x(90) @ Rot_z(90) @ Rot_z(-180) @ np.array([0, 0.62, 0]).T])

        #==================Open5DOF========================
        # w = np.array([[ 0, 0, 1],
        #               [ 0,-1, 0],
        #               [ 0,-1, 0],
        #               [ 0,-1, 0],
        #               [ 0, 0, 1]])
        
        # q = np.array([np.array([0, 0, 0]).T,
        #               np.array([0, 0, 0.306]).T,
        #               np.array([0, 0, 0.306]).T + Rot_x(90) @ Rot_z(40) @ np.array([0.096, 0.512, 0]).T,
        #               np.array([0, 0, 0.306]).T + Rot_x(90) @ Rot_z(40) @ np.array([0.096, 0.512, 0]).T + Rot_x(90) @ Rot_z(40) @ Rot_z(-40) @ np.array([0, 0.496, 0]).T,
        #               np.array([0, 0, 0.306]).T + Rot_x(90) @ Rot_z(40) @ np.array([0.096, 0.512, 0]).T + Rot_x(90) @ Rot_z(40) @ Rot_z(-40) @ np.array([0, 0.496, 0]).T + Rot_x(90) @ Rot_z(40) @ Rot_z(-40) @ Rot_z(-40) @ np.array([0, 0.12, 0]).T])
        
        v = -np.cross(w, q)
        return w,v

    def exp_twist(self, i, xi, theta):
        omega = xi[:3]
        v = xi[3:]
        omega_norm = np.linalg.norm(omega)

        if self.model.jnt_type[i] == 3: # Hinge
            omega_hat = skew(omega)
            R = (np.eye(3) +
                 np.sin(omega_norm * theta) / omega_norm * omega_hat +
                 (1 - np.cos(omega_norm * theta)) / (omega_norm ** 2) * np.dot(omega_hat, omega_hat))
            
            p = (np.eye(3) * theta +
                 (1 - np.cos(omega_norm * theta)) / (omega_norm ** 2) * omega_hat +
                 (theta - np.sin(omega_norm * theta) / omega_norm) / (omega_norm ** 2) * np.dot(omega_hat, omega_hat)).dot(v)
            
        if self.model.jnt_type[i] == 2:
            R = np.eye(3)
            p = theta * v

        return np.vstack((np.hstack((R, np.reshape(p, (3, 1)))), [0, 0, 0, 1]))
        
    
    def fkine(self, i, xi, theta):
        T = np.eye(4)
        omega = xi[:3]
        v = xi[3:]
        
        omega_hat = skew(omega)

        expm_w = expm(omega_hat*theta)
        g = (np.eye(3)*theta + (1-np.cos(theta))*omega
        + (theta-np.sin(theta)) * np.matmul(omega,omega))
        gv = np.matmul(g,v)
        expm_s = np.concatenate((expm_w,gv), axis=1)
        expm_s = np.concatenate((expm_s,[[0,0,0,1]]), axis=0)
        T = np.matmul(T,expm_s)

        return T

    def forward_kinematics(self, q):
        """
        q: 관절 각도 배열
        """
        
        #=================4DOF=========================
        # 초기 엔드 이펙터 좌표 (기준 좌표계에서의 위치)
        # T_ = []
        # T_.append(np.eye(4))

        # T_.append(np.eye(4))
        # T_[1][2,3] = 0.5
        # T_[1][:3,:3] = Rot_x(90) @ Rot_z(-10) 

        # T_.append(np.eye(4))
        # z = np.array([[0,0.8,0]])
        # T_[2][:3, 3] = T_[1][:3, 3] + T_[1][:3,:3] @ np.reshape(z,(3,))
        # T_[2][:3,:3] = T_[1][:3,:3] @ Rot_z(-10)

        # T_.append(np.eye(4))
        # z = np.array([[0,1.0,0]])
        # T_[3][:3,3] = T_[2][:3, 3] + T_[2][:3,:3] @ np.reshape(z,(3,))
        # T_[3][:3,:3] = T_[2][:3,:3] @ Rot_z(-10)

        # T_.append(np.eye(4))
        # z = np.array([[0,0.35,0]])
        # T_[4][:3,3] = T_[3][:3, 3] + T_[3][:3,:3] @ np.reshape(z,(3,))
        # T_[4][:3,:3] = T_[3][:3,:3]

        #=================Open4DOF=========================
        T_ = []
        T_.append(np.eye(4))

        T_.append(np.eye(4))
        T_[1][2,3] = 0.3825
        T_[1][:3,:3] = Rot_x(90) @ Rot_z(90) 

        T_.append(np.eye(4))
        z = np.array([[0.12,0.64,0]])
        T_[2][:3, 3] = T_[1][:3, 3] + T_[1][:3,:3] @ np.reshape(z,(3,))
        T_[2][:3,:3] = T_[1][:3,:3] @ Rot_z(-180)

        T_.append(np.eye(4))
        z = np.array([[0,0.62,0]])
        T_[3][:3,3] = T_[2][:3, 3] + T_[2][:3,:3] @ np.reshape(z,(3,))
        T_[3][:3,:3] = T_[2][:3,:3]

        T_.append(np.eye(4))
        z = np.array([[0,0.533,0]])
        T_[4][:3,3] = T_[3][:3, 3] + T_[3][:3,:3] @ np.reshape(z,(3,))
        T_[4][:3,:3] = T_[3][:3,:3] @ Rot_x(-90)
        
        #=================Open5DOF=========================
        # T_ = []
        # T_.append(np.eye(4))

        # T_.append(np.eye(4))
        # T_[1][2,3] = 0.306
        # T_[1][:3,:3] = Rot_x(90) @ Rot_z(40) 

        # T_.append(np.eye(4))
        # z = np.array([[0.096,0.512,0]])
        # T_[2][:3, 3] = T_[1][:3, 3] + T_[1][:3,:3] @ np.reshape(z,(3,))
        # T_[2][:3,:3] = T_[1][:3,:3] @ Rot_z(-40)

        # T_.append(np.eye(4))
        # z = np.array([[0,0.496,0]])
        # T_[3][:3,3] = T_[2][:3, 3] + T_[2][:3,:3] @ np.reshape(z,(3,))
        # T_[3][:3,:3] = T_[2][:3,:3] @ Rot_z(-40)

        # T_.append(np.eye(4))
        # z = np.array([[0,0.12,0]])
        # T_[4][:3,3] = T_[3][:3, 3] + T_[3][:3,:3] @ np.reshape(z,(3,))
        # T_[4][:3,:3] = T_[3][:3,:3] @ Rot_x(-90)

        # T_.append(np.eye(4))
        # z = np.array([[0,0,0.2096]])
        # T_[5][:3,3] = T_[4][:3, 3] + T_[4][:3,:3] @ np.reshape(z,(3,))
        # T_[5][:3,:3] = T_[4][:3,:3]
        
        w,v = self.get_first_wv()

        # 각 joint의 twist 벡터를 정의 (실제 로봇 돌릴 때, 여기 수정)
        twists = np.hstack((w,v))

        # POE 방식에 따른 forward kinematics 계산
        T = np.eye(4)
        for i, xi in enumerate(twists):
            T = np.dot(T, self.exp_twist(i, xi, q[i]))
            T_[i + 1] = np.dot(T,T_[i + 1])

        self.R_lnk = []
        self.P_lnk = []
        for i in range(self.model.njnt + 1):
            self.R_lnk.append(T_[i][:3,:3])
            self.P_lnk.append(T_[i][:3,3])

        self.P_EE = self.P_lnk[-1]
        self.R_EE = self.R_lnk[-1]

        return self.P_EE, self.R_EE, self.P_lnk, self.R_lnk
    
    def get_jnt_axis(self):
        w,v = self.get_first_wv()

        joint_axis = np.zeros((self.model.njnt, 3))

        for i in range(self.model.njnt):
            joint_axis[i,:] = self.R_lnk[i] @ np.reshape(w[0],(3,))

        return joint_axis

    def get_jacobian(self, joint_positions, joint_axes, end_effector_pos):
        """
        자코비안 계산 함수
        joint_positions: 각 관절의 위치 리스트 (Nx3 배열) -> P_lnk
        joint_axes: 각 관절의 회전축 리스트 (Nx3 배열) -> R_lnk*w
        end_effector_pos: 엔드 이펙터 위치 (3x1 벡터) -> P_EE
        joint_types: 관절 타입 리스트 (0=프리스매틱, 1=회전) -> m.jnt_type
        """
        num_joints = self.model.njnt
        
        # 선형 및 각 자코비안 초기화 (6 x N 자코비안)
        J_p = np.zeros((3, num_joints))
        J_r = np.zeros((3, num_joints))
        
        for i in range(num_joints):
            joint_pos = joint_positions[i]
            joint_axis = joint_axes[i]
            
            if self.model.jnt_type[i] == 3:  # 회전 관절
                J_p[:, i] = np.cross(joint_axis, (end_effector_pos - joint_pos))
                J_r[:, i] = joint_axis
            elif self.model.jnt_type[i] == 2:  # 프리스매틱 관절
                J_p[:, i] = joint_axis
                J_r[:, i] = np.zeros(3)

        for i in range(0,num_joints):
            joint_pos = self.data.body_xpos[i + 1]
            joint_axis = self.data.xaxis[i]
            
            if self.model.jnt_type[i] == 3:  # 회전 관절
                J_p[:, i] = np.cross(joint_axis, (self.data.body_xpos[-1] - joint_pos))
                J_r[:, i] = joint_axis
            elif self.model.jnt_type[i] == 2:  # 프리스매틱 관절
                J_p[:, i] = joint_axis
                J_r[:, i] = np.zeros(3)
        
        return J_p, J_r
    
    # def get_rot(self):
    #     rot = [None] * (self.model.njnt + 1)
    #     rot[0] = Rot_z(self.data.qpos[0] * 180 / pi)
    #     rot[1] = rot[0] @ Rot_x(90) @ Rot_z(self.data.qpos[1] * 180 / pi)
    #     rot[2] = rot[1] @ Rot_z(self.data.qpos[2] * 180 / pi)
    #     rot[3] = rot[2] @ Rot_z(self.data.qpos[3] * 180 / pi)
    #     rot[4] = rot[3] @ Rot_z(-90) @ Rot_x(-90)

    #     return rot

