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
somedata = pd.read_excel(io, sheet_name='Sheet2', usecols='P', nrows=16,
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
# 压杆与吊臂根部接头距离
dist_beam = somedata.loc[11, '参数']
# A塔高度
a_high = somedata.loc[12, '参数']
# A塔下宽
a_width_down = somedata.loc[13, '参数']
# A塔上宽
a_width_up= somedata.loc[14, '参数']
# A塔跨度
a_dist = somedata.loc[15, '参数']
# A塔截面
AW = atower.loc[0, '宽']  # 宽
AH = atower.loc[0, '高']  # 高
AT1 = atower.loc[0, '上下厚']   # 上下
AT2 = atower.loc[0, '中厚']   # 中
# 头部滑轮轴直径
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

# 定义头部板
s += f'SECTYPE,{section_num + 2},SHELL' + '\n'
s += f"SECDATA,{head_plate}" + '\n'

# 定义滑轮轴
s += f'SECTYPE,{section_num + 3},BEAM,CSOLID,,0' + '\n'
s += 'SECOFFSET,CENT' + '\n'
s += f"SECDATA,{head_pin/2}" + '\n'

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
s += '!head beam \n'
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

# 第一节吊臂头部四个节点
s += f'N,{7+(db1_segm-1)*4},{db1_b2/2},{db1_h2/2},{db1_len}' + '\n'
s += f'N,{8+(db1_segm-1)*4},{-db1_b2/2},{db1_h2/2},{db1_len}' + '\n'
s += f'N,{9+(db1_segm-1)*4},{db1_b2/2},{-db1_h2/2},{db1_len}' + '\n'
s += f'N,{10+(db1_segm-1)*4},{-db1_b2/2},{-db1_h2/2},{db1_len}' + '\n'
################# 中间节，节数=dbnum-2
s += '!center beam \n'
# 起始节点
start_node_1 = 7+(db1_segm-1)*4   # +x +y
start_node_2 = 8+(db1_segm-1)*4   # -x +y
start_node_3 = 9+(db1_segm-1)*4   # +x -y
start_node_4 = 10+(db1_segm-1)*4   # -x -y
start_z = db1_len
# 根据分段数均分
for i in range(2,dbnum):
    # 逐节建模
    # print(f'中间节{i}建模.')
    s += f'!center beam {i} \n'
    # 第i节吊臂，i范围从2到dbnum-1
    # 长度
    dbi_len = data_length.loc[i, '长度']
    # 根部宽度
    dbi_b1 = data_length.loc[i, '根部宽度']
    # 头部宽度
    dbi_b2 = data_length.loc[i, '头部宽度']
    # 根部高度, 此节为0
    dbi_h1 = data_length.loc[i, '根部高度']
    # 头部高度
    dbi_h2 = data_length.loc[i, '头部高度']
    # 分段数
    dbi_segm = data_length.loc[i, '分段数']
    # 该节吊臂新建节点总数为8*dbi_segm
    # print(f'第{i}节长度{dbi_len},分段数{dbi_segm},新建节点总数{8*dbi_segm}')
    for k in range(1,2*dbi_segm+1):
        s += f'N,{start_node_1+4*k},{(1-k/dbi_segm/2)*(dbi_b1-dbi_b2)/2+dbi_b2/2},{(1-k/dbi_segm/2)*(dbi_h1-dbi_h2)/2+dbi_h2/2},{start_z+k*dbi_len/dbi_segm/2}' + '\n'  # +x +y
        s += f'N,{start_node_2+4*k},{-(1-k/dbi_segm/2)*(dbi_b1-dbi_b2)/2-dbi_b2/2},{(1-k/dbi_segm/2)*(dbi_h1-dbi_h2)/2+dbi_h2/2},{start_z+k*dbi_len/dbi_segm/2}' + '\n'  # -x +y
        s += f'N,{start_node_3+4*k},{(1-k/dbi_segm/2)*(dbi_b1-dbi_b2)/2+dbi_b2/2},{-(1-k/dbi_segm/2)*(dbi_h1-dbi_h2)/2-dbi_h2/2},{start_z+k*dbi_len/dbi_segm/2}' + '\n'  # +x -y
        s += f'N,{start_node_4+4*k},{-(1-k/dbi_segm/2)*(dbi_b1-dbi_b2)/2-dbi_b2/2},{-(1-k/dbi_segm/2)*(dbi_h1-dbi_h2)/2-dbi_h2/2},{start_z+k*dbi_len/dbi_segm/2}' + '\n'  # -x -y
    start_node_1 = start_node_1+8*dbi_segm
    start_node_2 = start_node_2+8*dbi_segm
    start_node_3 = start_node_3+8*dbi_segm
    start_node_4 = start_node_4+8*dbi_segm
    start_z = start_z + dbi_len

################# 头部节，包括头部滑轮轴，拉索点
# 起始节点为start_node_1-2-3-4, 起始Z坐标为start_z
# 第dbnum节吊臂，即最前面的头部节
# 头部吊臂分段间隔按上下面的头尾宽度做等比数列，计算出公比。q=(b/a)**(1/n)
# hn=h*b*(1-1/(k**n))/(b-a)
s += '!head beam \n'
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
q = (head_b1/head_b2)**(1/(head_segm*2))

for i in range(1,2*head_segm+1):
    # 头部吊臂
    # print('头部吊臂建模')
    s += f'N,{start_node_1+4*i},{(head_b1/(q**i))/2},{(head_h1-head_b1*head_h1*(1-1/(q**i))*(1-head_h2/head_h1)/(head_b1-head_b2))/2},{start_z+head_len*head_b1*(1-1/(q**i))/(head_b1-head_b2)}' + '\n'  # +x +y
    s += f'N,{start_node_2+4*i},{-(head_b1/(q**i))/2},{(head_h1-head_b1*head_h1*(1-1/(q**i))*(1-head_h2/head_h1)/(head_b1-head_b2))/2},{start_z+head_len*head_b1*(1-1/(q**i))/(head_b1-head_b2)}' + '\n'
    s += f'N,{start_node_3+4*i},{(head_b1/(q**i))/2},{-(head_h1-head_b1*head_h1*(1-1/(q**i))*(1-head_h2/head_h1)/(head_b1-head_b2))/2},{start_z+head_len*head_b1*(1-1/(q**i))/(head_b1-head_b2)}' + '\n'
    s += f'N,{start_node_4+4*i},{-(head_b1/(q**i))/2},{-(head_h1-head_b1*head_h1*(1-1/(q**i))*(1-head_h2/head_h1)/(head_b1-head_b2))/2},{start_z+head_len*head_b1*(1-1/(q**i))/(head_b1-head_b2)}' + '\n'

# 最前端的4个node
start_node_1 = start_node_1+8*head_segm   # +x +y
start_node_2 = start_node_2+8*head_segm   # -x +y
start_node_3 = start_node_3+8*head_segm   # +x -y
start_node_4 = start_node_4+8*head_segm   # -x -y
top_node = start_node_4
start_z_max = start_z + head_len  # 吊臂最前端z坐标值 
# 定义吊臂头部轴节点,滑轮在偏X轴正向位置
s += '!add some nodes at top \n'
s += f'N,{top_node+1},{head_b2/2},0,{start_z_max}' + '\n'
s += f'N,{top_node+2},{head_b2/2-head_pulley_offset},0,{start_z_max}' + '\n'
s += f'N,{top_node+3},{-head_b2/2},0,{start_z_max}' + '\n'

# 定义头部拉索点
s += f'N,{top_node+4},{(head_b1/(q**9))/2},{(head_h1-head_b1*head_h1*(1-1/(q**9))*(1-head_h2/head_h1)/(head_b1-head_b2))/2+200},{start_z+head_len*head_b1*(1-1/(q**9))/(head_b1-head_b2)}' + '\n'
s += f'N,{top_node+5},{-(head_b1/(q**9))/2},{(head_h1-head_b1*head_h1*(1-1/(q**9))*(1-head_h2/head_h1)/(head_b1-head_b2))/2+200},{start_z+head_len*head_b1*(1-1/(q**9))/(head_b1-head_b2)}' + '\n'

# 定义头部辅助节点6个
s += f'N,{top_node+6},{(head_b1/(q**9))/2},0,{start_z+head_len*head_b1*(1-1/(q**9))/(head_b1-head_b2)}' + '\n'
s += f'N,{top_node+7},{-(head_b1/(q**9))/2},0,{start_z+head_len*head_b1*(1-1/(q**9))/(head_b1-head_b2)}' + '\n'
s += f'N,{top_node+8},{(head_b1/(q**10))/2},0,{start_z+head_len*head_b1*(1-1/(q**10))/(head_b1-head_b2)}' + '\n'
s += f'N,{top_node+9},{-(head_b1/(q**10))/2},0,{start_z+head_len*head_b1*(1-1/(q**10))/(head_b1-head_b2)}' + '\n'
s += f'N,{top_node+10},{(head_b1/(q**11))/2},0,{start_z+head_len*head_b1*(1-1/(q**11))/(head_b1-head_b2)}' + '\n'
s += f'N,{top_node+11},{-(head_b1/(q**11))/2},0,{start_z+head_len*head_b1*(1-1/(q**11))/(head_b1-head_b2)}' + '\n'

# 吊臂的Node 创建完毕
# 先旋转所有吊臂节点再进行下一步建模
s += 'CSYS,0 \n'
s += f'CLOCAL,1001,0,0,0,0,0,{angle},0' + '\n'
s += '''CSYS,1001
TRANSFER,0,0,ALL
CSYS,0
CSDELE,ALL
'''
###########  定义A塔节点
ata_node = top_node+11
s += f'N,{ata_node+1},{a_width_down/2},0,{-dist_beam}' + '\n'
s += f'N,{ata_node+2},{-a_width_down/2},0,{-dist_beam}' + '\n'
s += f'N,{ata_node+3},{a_width_down/2},0,{-dist_beam-a_dist}' + '\n'
s += f'N,{ata_node+4},{-a_width_down/2},0,{-dist_beam-a_dist}' + '\n'
s += f'N,{ata_node+5},{(a_width_up+a_width_down)/4},{a_high/2},{-dist_beam-a_dist/2}' + '\n'
s += f'N,{ata_node+6},{-(a_width_up+a_width_down)/4},{a_high/2},{-dist_beam-a_dist/2}' + '\n'
s += f'N,{ata_node+7},{(a_width_up+a_width_down)/4},{a_high/2},{-dist_beam-a_dist}' + '\n'
s += f'N,{ata_node+8},{-(a_width_up+a_width_down)/4},{a_high/2},{-dist_beam-a_dist}' + '\n'
s += f'N,{ata_node+9},{a_width_up/2},{a_high},{-dist_beam-a_dist}' + '\n'
s += f'N,{ata_node+10},{-a_width_up/2},{a_high},{-dist_beam-a_dist}' + '\n'

############  定义单元
s += '!define elements \n'
# 吊臂每小节单元分开定义，并单独存储单元编号，主弦编号，区分上下弦
###### 根部节
# 单元
s += 'TYPE,1' + '\n'
# 材料
s += 'MAT,1' + '\n'
# 截面，上弦
sec_num_temp = data_secnum.loc[1,'上弦']
s += f'SECNUM,{sec_num_temp}' + '\n'

s += 'EN,1,1,7' + '\n'
for i in range(2,db1_segm+1):
    s += f'EN,{i},{7+(i-2)*4},{11+(i-2)*4}' + '\n'

s += f'EN,{db1_segm+1},2,8' + '\n'
for i in range(2,db1_segm+1):
    s += f'EN,{db1_segm+i},{8+(i-2)*4},{12+(i-2)*4}' + '\n'
# 截面，下弦
sec_num_temp = data_secnum.loc[1,'下弦']
s += f'SECNUM,{sec_num_temp}' + '\n'
# head_segm*2
s += f'EN,{db1_segm*2+1},1,5' + '\n'
for i in range(2,db1_segm+2):
    s += f'EN,{db1_segm*2+i},{5+(i-2)*4},{9+(i-2)*4}' + '\n'

# head_segm*3+1
s += f'EN,{db1_segm*3+2},2,6' + '\n'
for i in range(2,db1_segm+2):
    s += f'EN,{db1_segm*3+1+i},{6+(i-2)*4},{10+(i-2)*4}' + '\n'

# node number   head_segm*4+2

# 截面，横腹杆，即上下面
sec_num_temp = data_secnum.loc[1,'横腹杆']
s += f'SECNUM,{sec_num_temp}' + '\n'

s += f'EN,{db1_segm*4+3},1,3' + '\n'
s += f'EN,{db1_segm*4+4},3,8' + '\n'
s += f'EN,{db1_segm*4+5},2,3' + '\n'
s += f'EN,{db1_segm*4+6},3,7' + '\n'

node_num = db1_segm*4+6
temp = 0
# 上平面
for i in range(1,db1_segm+1):
    s += f'EN,{node_num+(i-1)*2+1},{7+(i-1)*4},{8+(i-1)*4}' + '\n'
    temp = temp + 1
    if i<db1_segm:
        if (i%2)==0: # i是偶数
            s += f'EN,{node_num+(i-1)*2+2},{8+(i-1)*4},{7+i*4}' + '\n'
            temp = temp + 1
        else:
            s += f'EN,{node_num+(i-1)*2+2},{7+(i-1)*4},{8+i*4}' + '\n'
            temp = temp + 1

node_num = node_num + temp

s += f'EN,{node_num+1},1,4' + '\n'
s += f'EN,{node_num+2},4,6' + '\n'
s += f'EN,{node_num+3},2,4' + '\n'
s += f'EN,{node_num+4},4,5' + '\n'

node_num = node_num + 4
temp = 0
# 下平面
for i in range(1,db1_segm+2):
    s += f'EN,{node_num+(i-1)*2+1},{5+(i-1)*4},{6+(i-1)*4}' + '\n'
    temp = temp + 1
    if i<(db1_segm+1):
        if (i%2)==0: # i是偶数
            s += f'EN,{node_num+(i-1)*2+2},{5+(i-1)*4},{6+i*4}' + '\n'
            temp = temp + 1
        else:
            s += f'EN,{node_num+(i-1)*2+2},{6+(i-1)*4},{5+i*4}' + '\n'
            temp = temp + 1

node_num = node_num + temp
# 截面，侧腹杆，即左右面
sec_num_temp = data_secnum.loc[1,'侧腹杆']
s += f'SECNUM,{sec_num_temp}' + '\n'
temp = 0
s += f'EN,{node_num+1},7,5' + '\n'
temp = temp+1
for i in range(1,db1_segm):
    s += f'EN,{node_num+1+(i-1)*2+1},{7+(i-1)*4},{9+(i-1)*4}' + '\n'
    s += f'EN,{node_num+1+(i-1)*2+2},{9+(i-1)*4},{11+(i-1)*4}' + '\n'
    temp = temp+2

node_num = node_num + temp
s += f'EN,{node_num+1},{7+(db1_segm-1)*4},{9+(db1_segm-1)*4}' + '\n'

node_num = node_num + 1

temp = 0
s += f'EN,{node_num+1},8,6' + '\n'
temp = temp+1
for i in range(1,db1_segm):
    s += f'EN,{node_num+1+(i-1)*2+1},{8+(i-1)*4},{10+(i-1)*4}' + '\n'
    s += f'EN,{node_num+1+(i-1)*2+2},{10+(i-1)*4},{12+(i-1)*4}' + '\n'
    temp = temp+2

node_num = node_num + temp
s += f'EN,{node_num+1},{8+(db1_segm-1)*4},{10+(db1_segm-1)*4}' + '\n'

node_num = node_num + 1

# 截面，斜腹杆，该节吊臂前端一根斜的腹杆
sec_num_temp = data_secnum.loc[1,'斜腹杆']
s += f'SECNUM,{sec_num_temp}' + '\n'
s += f'EN,{node_num+1},{8+(db1_segm-1)*4},{9+(db1_segm-1)*4}' + '\n'
node_num = node_num + 1

######## 根部第一节吊臂单元生成结束
# 单元编号收集。 

###### 中间节
for i in range(2,dbnum):
    # 中间节程序化生成单元2到dbnum-1节
    print(f'第{i}节吊臂')





###### 头部节


###### 拉索


###### A塔

############  定义边界条件



############  定义载荷


############  求解


############  后处理
s +='''
/PNUM,ELEM,1
EPLOT
/REPLOT
'''
f = open(mac_name, 'w')
f.write(s)
f.close()
print('命令流生成完毕！')
