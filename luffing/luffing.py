# coding=utf-8
# 动臂吊臂建模宏命令生成
# 注意：必须先按luffingbeam.xlsx格式填充吊臂设计的各项参数
# 2021-05-08开始编写
import pandas as pd
import os


os.chdir(os.path.dirname(__file__))
io = r'luffingbeam.xlsx'
# ==========================
atower = pd.read_excel(io, sheet_name='Sheet2', usecols='J:M', nrows=1,
                            converters={'宽': float, '高': float, '上下厚': float, '中厚': float},
                            index_col=None)
somedata = pd.read_excel(io, sheet_name='Sheet2', usecols='P', nrows=11,
                            converters={'参数': float},
                            index_col=None)

# 吊臂节数
dbnum = int(somedata.loc[4, '参数'])
# 最大载荷, 单位:吨
maxload = somedata.loc[5, '参数']
# 钩头和钢丝绳载荷, 单位:吨
toolload = somedata.loc[6, '参数']
# 吊臂头部等效水平力，单位：吨
headforce = somedata.loc[7, '参数']
# 吊臂角度，单位：度
angle = somedata.loc[8, '参数']
# 重力加速度，初次空载计算按9800，对比实际重量，修改增大系数
gravity = somedata.loc[9, '参数']
# 输出宏文件的文件名
mac_name = 'luffingbeam.mac'
# 宏文件计算输出的txt结果文件名
txt_name = 'luffingres'
# 截面总数量
section_num = int(somedata.loc[10, '参数'])
# A塔截面
AW = atower.loc[0, '宽']  # 宽
AH = atower.loc[0, '高']  # 高
AT1 = atower.loc[0, '上下厚']   # 上下
AT2 = atower.loc[0, '中厚']   # 中
# 头部滑轮轴截面
head_pin = somedata.loc[0, '参数']
# 拉索截面
inhaul_cable = 3.14 * (somedata.loc[1, '参数'] ** 2) / 4
# 头部板厚
head_plate = somedata.loc[2, '参数']
# 滑轮左侧偏移
head_pulley_offset = somedata.loc[3, '参数']
# ==========================

data_secnum = pd.read_excel(io, sheet_name='Sheet1', usecols='A:F', nrows=dbnum,
                            converters={'吊臂序号': int, '上弦': int, '横腹杆': int,
                                        '斜腹杆': int, '侧腹杆': int, '下弦': int},
                            index_col=[0])
data_section = pd.read_excel(io, sheet_name='Sheet1', usecols='H:O', nrows=section_num,
                             converters={'截面序号': int, '截面类型': int, '参数1': float, '参数2': float,
                                         '参数3': float, '参数4': float, '参数5': float, '参数6': float},
                             index_col=[0])
data_length = pd.read_excel(io, sheet_name='Sheet2', usecols='A:G', nrows=dbnum,
                            converters={'吊臂号': int, '长度': float, '根部宽度': float, '头部宽度': float,
                                        '根部高度': float, '头部高度': float, '分段数': int},
                            index_col=[0])


# 使用变量s保存所有命令流文本
# 1、首先输出通用头部命令
s = '''/CLEAR
/UIS,MSGPOP,3
/PREP7
*AFUN,DEG
ET,1,BEAM188
MP,EX,1,2.1E5
MP,PRXY,1,0.3
MP,DENS,1,7.85E-9
'''
s += 'ET,2,LINK10' + '\n'
s += f'R,2,{inhaul_cable}' + '\n'
s += '''MP,EX,2,1.05E5    
MP,DENS,2,7.85E-9
KEYOPT,2,3,0
ET,3,SHELL181
'''
# 2、集中定义所需梁单元截面
# 定义吊臂上的截面：从data_section逐行读取，根据截面类型选择适合的定义命令
for i in range(1, section_num + 1):
    if data_section.loc[i, '截面类型'] == 1:  # H型
        s += f'SECTYPE,{i},BEAM,I,,0' + '\n'
        s += 'SECOFFSET,CENT' + '\n'
        s += f"SECDATA,{data_section.loc[i, '参数2']},{data_section.loc[i, '参数1']}," \
             f"{data_section.loc[i, '参数3']},{data_section.loc[i, '参数4']}," \
             f"{data_section.loc[i, '参数5']},{data_section.loc[i, '参数6']}" + '\n'

    elif data_section.loc[i, '截面类型'] == 2:  # 方管
        s += f'SECTYPE,{i},BEAM,HREC,,0' + '\n'
        s += 'SECOFFSET,CENT' + '\n'
        s += f"SECDATA,{data_section.loc[i, '参数2']},{data_section.loc[i, '参数1']}," \
             f"{data_section.loc[i, '参数5']},{data_section.loc[i, '参数6']}," \
             f"{data_section.loc[i, '参数4']},{data_section.loc[i, '参数3']}" + '\n'

    elif data_section.loc[i, '截面类型'] == 3:  # 圆管
        s += f'SECTYPE,{i},BEAM,CTUBE,,0' + '\n'
        s += 'SECOFFSET,CENT' + '\n'
        temp1 = data_section.loc[i, '参数1'] / 2 - data_section.loc[i, '参数2']
        temp2 = data_section.loc[i, '参数1'] / 2
        s += f"SECDATA,{temp1},{temp2}" + '\n'

    else:  # 实心矩形
        s += f'SECTYPE,{i},BEAM,RECT,,0' + '\n'
        s += 'SECOFFSET,CENT' + '\n'
        s += f"SECDATA,{data_section.loc[i, '参数2']},{data_section.loc[i, '参数1']}" + '\n'

# 定义A塔的截面
s += f'SECTYPE,{section_num + 1},BEAM,I,,0' + '\n'
s += 'SECOFFSET,CENT' + '\n'
s += f"SECDATA,{AW},{AW},{AH},{AT1},{AT1},{AT2}" + '\n'
# 3、吊臂建模，先定义节点，然后选择对应的截面建立梁单元，同时将需要提取的节点编号、单元编号保存到列表中
# 吊臂逐小节建节点NODE，并赋截面
# 吊臂先零度位置建模，然后整体旋转angle = somedata.loc[8, '参数']
# 吊臂根部节，头部节，中间节，分别用不同算法
# 沿吊臂长度方向为Z，竖直向上为Y，侧向为X

################# 根部节
# 直接根据分段数。模式化建模。上平面均分。
# 长度
db1_len = data_length.loc[1, '长度']
# 根部宽度
db1_b1 = data_length.loc[1, '根部宽度']
# 头部宽度
db1_b2 = data_length.loc[1, '头部宽度']
# 根部高度, 此节为0
db1_h1 = data_length.loc[1, '根部高度']
# 头部高度
db1_h2 = data_length.loc[1, '头部高度']
# 分段数
db1_segm = data_length.loc[1, '分段数']

s += f'N,1,{db1_b1/2},0,0' + '\n'
s += f'N,2,{-db1_b1/2},0,0' + '\n'
s += f'N,3,0,{db1_h2/2/(db1_segm*2)},{db1_len/(db1_segm*2)}' + '\n'
s += f'N,4,0,{-db1_h2/2/(db1_segm*2)},{db1_len/(db1_segm*2)}' + '\n'

s += f'N,5,{(1-1/db1_segm)*(db1_b1-db1_b2)/2+db1_b2/2},{-db1_h2/2/db1_segm},{db1_len/db1_segm}' + '\n'
s += f'N,6,{-(1-1/db1_segm)*(db1_b1-db1_b2)/2-db1_b2/2},{-db1_h2/2/db1_segm},{db1_len/db1_segm}' + '\n'

for i in range(1,db1_segm):
    # up
    s += f'N,{7+(i-1)*4},{(1-i/db1_segm)*(db1_b1-db1_b2)/2+db1_b2/2},{db1_h2*i/2/db1_segm},{db1_len*i/db1_segm}' + '\n'
    s += f'N,{8+(i-1)*4},{-(1-i/db1_segm)*(db1_b1-db1_b2)/2-db1_b2/2},{db1_h2*i/2/db1_segm},{db1_len*i/db1_segm}' + '\n'
    # down
    s += f'N,{9+(i-1)*4},{(1-(i*2-1)/(db1_segm*2))*(db1_b1-db1_b2)/2+db1_b2/2},{-db1_h2*(i*2+1)/2/(db1_segm*2)},{db1_len*(i*2+1)/(db1_segm*2)}' + '\n'
    s += f'N,{10+(i-1)*4},{-(1-(i*2-1)/(db1_segm*2))*(db1_b1-db1_b2)/2-db1_b2/2},{-db1_h2*(i*2+1)/2/(db1_segm*2)},{db1_len*(i*2+1)/(db1_segm*2)}' + '\n'

s += f'N,{7+(db1_segm-1)*4},{db1_b2/2},{db1_h2/2},{db1_len}' + '\n'
s += f'N,{8+(db1_segm-1)*4},{-db1_b2/2},{db1_h2/2},{db1_len}' + '\n'
s += f'N,{9+(db1_segm-1)*4},{db1_b2/2},{-db1_h2/2},{db1_len}' + '\n'
s += f'N,{10+(db1_segm-1)*4},{-db1_b2/2},{-db1_h2/2},{db1_len}' + '\n'
################# 中间节，节数=dbnum-2
# 根据分段数均分。
for i in range(2,dbnum-1):
    # 逐节建模
    print(f'中间节{i}建模.')



################# 头部节，包括头部滑轮轴，拉索点

# 长度
head_len = data_length.loc[dbnum, '长度']
# 根部宽度
head_b1 = data_length.loc[dbnum, '根部宽度']
# 头部宽度
head_b2 = data_length.loc[dbnum, '头部宽度']
# 根部高度
head_h1 = data_length.loc[dbnum, '根部高度']
# 头部高度
head_h2 = data_length.loc[dbnum, '头部高度']
# 分段数
head_segm = data_length.loc[dbnum, '分段数']



f = open(mac_name, 'w')
f.write(s)
f.close()
print('命令流生成完毕！')
