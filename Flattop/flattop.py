# coding=utf-8
# 平臂吊臂建模宏命令生成
# 注意：必须先按beam.xlsx格式填充吊臂设计的各项参数
import pandas as pd

# ==========================
# 参数控制：吊臂幅度工况，端部载荷，重力加速度
# 吊臂数量，包括头部吊臂
dbnum = 9
# 最大幅度载荷，加载点在头部吊臂根部节点, 单位N
maxload = 376000
# 重力加速度，初次空载计算按9800，对比实际重量，修改增大系数
gravity = 9800 * 1.189
# 输出宏文件的文件名
mac_name = 'R90.mac'
# 宏文件计算输出的txt结果文件名
txt_name = 'R90res'
# 截面总数量
section_num = 53
# 吊臂总节档数
parts = 32
# ==========================
io = r'beam.xlsx'
data_secnum = pd.read_excel(io, sheet_name='Sheet1', usecols='A:H', nrows=parts,
                            converters={'吊臂序号': int, '节号': int, '上弦': int, '上横腹杆': int,
                                        '上斜腹杆': int, '中竖腹杆': int, '中斜腹杆': int, '下弦': int},
                            index_col=[0, 1])
data_section = pd.read_excel(io, sheet_name='Sheet1', usecols='J:Q', nrows=section_num,
                             converters={'截面序号': int, '截面类型': int, '参数1': float, '参数2': float,
                                         '参数3': float, '参数4': float, '参数5': float, '参数6': float},
                             index_col=[0])
data_length = pd.read_excel(io, sheet_name='Sheet1', usecols='AB:AH', nrows=dbnum,
                            converters={'吊臂号': int, '长度': float, '根部宽度': float, '头部宽度': float,
                                        '根部高度': float, '头部高度': float, '分段数': int},
                            index_col=[0])

# 引入一个全局变量NST，保存头部下弦节点号，作为下一节吊臂建模头部下弦的起始节点号
NST = 0  # 下弦节点编号
NSX = 0  # 下弦节点X坐标（下弦节点YZ坐标都为0）
DBN = 0  # 吊臂段数序号
xnode = []  # 下弦节点列表
shang1 = []  # 上弦单元列表，Y+侧
shang2 = []  # 上弦单元列表，Y-侧
xia = []  # 下弦单元列表
# 1、首先输出通用头部命令
s = '''/CLEAR
/PREP7
*AFUN,DEG
ET,1,BEAM188
MP,EX,1,2.1E5
MP,PRXY,1,0.3
MP,DENS,1,7.85E-9
'''
# 2、集中定义所需梁单元截面
# 定义截面：从data_section逐行读取，根据截面类型选择适合的定义命令
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
# 3、吊臂建模，先定义节点，然后选择对应的截面建立梁单元，同时将需要提取的节点编号、单元编号保存到列表中
# 吊臂逐小节建节点NODE，并赋截面，除头部吊臂
for i in range(1, dbnum):  # 吊臂号，视臂长而定
    L = data_length.loc[i, '长度']
    WB = data_length.loc[i, '根部宽度']
    WF = data_length.loc[i, '头部宽度']
    HB = data_length.loc[i, '根部高度']
    HF = data_length.loc[i, '头部高度']
    N = data_length.loc[i, '分段数']
    if i == 1:
        # 根部初始三个节点
        s += 'N,1,0,0,0' + '\n'
        s += f"N,2,0,{WB / 2},{HB}" + '\n'
        s += f"N,3,0,{-WB / 2},{HB}" + '\n'
        NST += 3  # 初始为0，现在是3

    for j in range(1, N + 1):
        # 第i节吊臂，第j段。
        DBN += 1
        # 上一节点编号，下弦，上弦+，上弦-,分别为：NST-2,NST-1,NST
        a = NST - 2
        b = NST - 1
        c = NST
        A = NST + 1
        B = NST + 2
        C = NST + 3
        NST += 3
        NSX += L / N
        if j == N:  # 保存每节吊臂头部下弦节点编号，以便提取位移结果
            xnode.append(A)

        s += f'N,{A},{NSX},0,0' + '\n'  # 下弦NODE
        s += f'N,{B},{NSX},{WB / 2 - j * (WB / 2 - WF / 2) / N},{HB - j * (HB - HF) / N}' + '\n'  # 上弦+Y向NODE
        s += f'N,{C},{NSX},{-WB / 2 + j * (WB / 2 - WF / 2) / N},{HB - j * (HB - HF) / N}' + '\n'  # 上弦-Y向NODE
        # 上弦
        s += 'TYPE,1' + '\n'
        s += 'MAT,1' + '\n'
        s += f"SECNUM,{data_secnum.loc[(i, j), '上弦']}" + '\n'
        s += f'E,{b},{B}' + '\n'  # 1x
        s += f'E,{c},{C}' + '\n'  # 2x
        x1 = 1 + (DBN - 1) * 9
        x2 = 2 + (DBN - 1) * 9
        shang1.append(x1)
        shang2.append(x2)
        # 上横腹杆
        s += f"SECNUM,{data_secnum.loc[(i, j), '上横腹杆']}" + '\n'
        s += f'E,{B},{C}' + '\n'
        # 上斜腹杆
        s += f"SECNUM,{data_secnum.loc[(i, j), '上斜腹杆']}" + '\n'
        if j % 2 == 0:
            s += f'E,{b},{C}' + '\n'
        else:
            s += f'E,{c},{B}' + '\n'
        # 中竖腹杆
        s += f"SECNUM,{data_secnum.loc[(i, j), '中竖腹杆']}" + '\n'
        s += f'E,{B},{A}' + '\n'
        s += f'E,{C},{A}' + '\n'
        # 中斜腹杆
        s += f"SECNUM,{data_secnum.loc[(i, j), '中斜腹杆']}" + '\n'
        s += f'E,{b},{A}' + '\n'
        s += f'E,{c},{A}' + '\n'
        # 下弦
        s += f"SECNUM,{data_secnum.loc[(i, j), '下弦']}" + '\n'
        s += f'E,{a},{A}' + '\n'  # 9x
        x9 = 9 + (DBN - 1) * 9
        xia.append(x9)

loadnode = NST - 2  # 加载节点编号
# 头部吊臂建模
L = data_length.loc[dbnum, '长度']
a = NST - 2
b = NST - 1
c = NST
A = NST + 1
NST += 1
NSX += L
s += f'N,{A},{NSX},0,0' + '\n'  # 下弦NODE
# 中斜腹杆
s += f"SECNUM,{data_secnum.loc[(dbnum, 1), '中斜腹杆']}" + '\n'
s += f'E,{b},{A}' + '\n'
s += f'E,{c},{A}' + '\n'
# 下弦
s += f"SECNUM,{data_secnum.loc[(dbnum, 1), '下弦']}" + '\n'
s += f'E,{a},{A}' + '\n'

# 定义约束
s += '''
D,1,ALL,0
D,2,ALL,0
D,3,ALL,0
'''
# 加载
s += f"F,{loadnode},FZ,-{maxload}" + '\n'
# 求解
s += '/SOLU' + '\n'
s += f'ACEL,,,{gravity}' + '\n'
s += '''
ALLSEL,ALL
NLGEOM,ON
SOLVE
/POST1
TP1=0
'''
s += f'*CFOPEN,{txt_name},txt,,Append' + '\n'
s += '''
*VWRITE,
('displacement/mm')
'''
for node in xnode:
    s += f'*GET,TP1,NODE,{node},U,Z' + '\n'
    s += '*VWRITE,TP1' + '\n'
    s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('ForceReaction/t')
*VWRITE,
('up-a-X/t')
'''
s += f'*GET,TP1,NODE,2,RF,FX' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'
s += '''
*VWRITE,
('up-a-Y/t')
'''
s += f'*GET,TP1,NODE,2,RF,FY' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'
s += '''
*VWRITE,
('up-a-Z/t')
'''
s += f'*GET,TP1,NODE,2,RF,FZ' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('up-b-X/t')
'''
s += f'*GET,TP1,NODE,3,RF,FX' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'
s += '''
*VWRITE,
('up-b-Y/t')
'''
s += f'*GET,TP1,NODE,3,RF,FY' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'
s += '''
*VWRITE,
('up-b-Z/t')
'''
s += f'*GET,TP1,NODE,3,RF,FZ' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('DOWN-X/t')
'''
s += f'*GET,TP1,NODE,1,RF,FX' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'
s += '''
*VWRITE,
('DOWN-Y/t')
'''
s += f'*GET,TP1,NODE,1,RF,FY' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'
s += '''
*VWRITE,
('DOWN-Z/t')
'''
s += f'*GET,TP1,NODE,1,RF,FZ' + '\n'
s += '*VWRITE,TP1/10000' + '\n'
s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('up-1-F/t')
'''
for elem in shang1:
    s += f'*GET,TP1,ELEM,{elem},SMISC,1' + '\n'
    s += '*VWRITE,TP1/10000' + '\n'
    s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('up-2-F/t')
'''
for elem in shang2:
    s += f'*GET,TP1,ELEM,{elem},SMISC,1' + '\n'
    s += '*VWRITE,TP1/10000' + '\n'
    s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('down-F/t')
'''
for elem in xia:
    s += f'*GET,TP1,ELEM,{elem},SMISC,1' + '\n'
    s += '*VWRITE,TP1/10000' + '\n'
    s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('up-1-S/MPa')
'''
for elem in shang1:
    s += f'*GET,TP1,ELEM,{elem},SMISC,31' + '\n'
    s += '*VWRITE,TP1' + '\n'
    s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('up-2-S/MPa')
'''
for elem in shang2:
    s += f'*GET,TP1,ELEM,{elem},SMISC,31' + '\n'
    s += '*VWRITE,TP1' + '\n'
    s += '(F13.2)' + '\n'

s += '''
*VWRITE,
('down-S/MPa')
'''
for elem in xia:
    s += f'*GET,TP1,ELEM,{elem},SMISC,31' + '\n'
    s += '*VWRITE,TP1' + '\n'
    s += '(F13.2)' + '\n'

s += '*CFCLOS' + '\n'

f = open(mac_name, 'w')
f.write(s)
f.close()
