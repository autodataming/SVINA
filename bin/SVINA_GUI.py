import os
import subprocess
import rdkit
from rdkit import Chem
from rdkit.Chem import Draw
import csv
import json
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox
from tkinter.ttk import Progressbar
import threading
import meeko
import sys 


class DockingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("分子对接工具")


        install_dir = os.path.dirname(os.path.abspath(__file__))
        meeko_dir = os.path.dirname(meeko.__file__)


        # 配置路径
        self.vina_executable = os.path.join(install_dir,"vina.exe")
 
        python_path = sys.executable
        python_dir = os.path.dirname(python_path)
        # C:\Users\Lenovo\AppData\Roaming\SVINA\env\Library\bin
        self.openbabel_executable = os.path.join(python_dir,"library","bin","obabel.exe")
        
        self.prepare_ligand_script =  os.path.join(meeko_dir,"cli",  "mk_prepare_ligand.py")
        self.export_script =     os.path.join(meeko_dir,"cli",        "mk_export.py")
        
        # 创建UI组件
        self.create_widgets()

    def create_widgets(self):
        # 标签
        self.workdir_label = Label(self.root, text="工作目录:")
        self.workdir_label.grid(row=0, column=0, padx=10, pady=10)
        
        # 输入框
        self.workdir_entry = Entry(self.root, width=50)
        self.workdir_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # 按钮
        self.browse_button = Button(self.root, text="浏览", command=self.browse_directory)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.receptor_label = Label(self.root, text="受体文件 (PDBQT):")
        self.receptor_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.receptor_entry = Entry(self.root, width=50)
        self.receptor_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.receptor_button = Button(self.root, text="浏览", command=self.browse_receptor)
        self.receptor_button.grid(row=1, column=2, padx=10, pady=10)

        self.ligand_label = Label(self.root, text="配体文件 (CDX):")
        self.ligand_label.grid(row=2, column=0, padx=10, pady=10)
        
        self.ligand_entry = Entry(self.root, width=50)
        self.ligand_entry.grid(row=2, column=1, padx=10, pady=10)
        
        self.ligand_button = Button(self.root, text="浏览", command=self.browse_ligand)
        self.ligand_button.grid(row=2, column=2, padx=10, pady=10)

        self.config_label = Label(self.root, text="配置文件 (BOX):")
        self.config_label.grid(row=3, column=0, padx=10, pady=10)
        
        self.config_entry = Entry(self.root, width=50)
        self.config_entry.grid(row=3, column=1, padx=10, pady=10)
        
        self.config_button = Button(self.root, text="浏览", command=self.browse_config)
        self.config_button.grid(row=3, column=2, padx=10, pady=10)
        
        # 进度条
        self.progress_bar = Progressbar(self.root, length=300, mode='determinate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
        
        # 运行按钮
        self.run_button = Button(self.root, text="开始运行", command=self.run_docking)
        self.run_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.workdir_entry.delete(0, 'end')
            self.workdir_entry.insert(0, directory)
    
    def browse_receptor(self):
        receptor_file = filedialog.askopenfilename(filetypes=[("PDBQT Files", "*.pdbqt")])
        if receptor_file:
            self.receptor_entry.delete(0, 'end')
            self.receptor_entry.insert(0, receptor_file)
    
    def browse_ligand(self):
        ligand_file = filedialog.askopenfilename(filetypes=[("CDX Files", "*.cdx")])
        if ligand_file:
            self.ligand_entry.delete(0, 'end')
            self.ligand_entry.insert(0, ligand_file)
    
    def browse_config(self):
        config_file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if config_file:
            self.config_entry.delete(0, 'end')
            self.config_entry.insert(0, config_file)
    
    def run_docking(self):
        workdir = self.workdir_entry.get()
        output_dir = os.path.join(workdir, "docking_results") 

        # 创建中间文件存储目录
        intermediate_dir = os.path.join(output_dir, "intermediate_files")
        if not os.path.exists(intermediate_dir):
            os.makedirs(intermediate_dir)

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        receptor_pdbqt = self.receptor_entry.get()
        ligand_cdx = self.ligand_entry.get()
        config_file = self.config_entry.get()

        if not all([workdir, receptor_pdbqt, ligand_cdx, config_file]):
            messagebox.showerror("错误", "请确保所有文件路径已选择！")
            return
        
        # 更新UI
        self.progress_bar['value'] = 0
        self.root.update_idletasks()

        # 运行过程
        threading.Thread(target=self.run_docking_process, args=(output_dir, receptor_pdbqt, ligand_cdx, config_file, intermediate_dir)).start()

    def run_docking_process(self, workdir, receptor_pdbqt, ligand_cdx, config_file, intermediate_dir):
        try:
            # 打印调试信息
            print(f"工作目录: {workdir}")
            print(f"受体文件: {receptor_pdbqt}")
            print(f"配体文件: {ligand_cdx}")
            print(f"配置文件: {config_file}")

            # 步骤 1: 用 Open Babel 将 CDX 转换为 SDF 文件
            print("正在将 CDX 文件转换为 SDF 文件...")
            sdf_file = os.path.join(workdir, "ligands.sdf")
            command = [
                self.openbabel_executable, ligand_cdx,
                "-O", sdf_file,
                "--gen3d"
            ]
            print("执行命令:", " ".join(command))
            subprocess.run(command, check=True)
            print("转换成功！")

            # 更新进度条
            self.progress_bar['value'] = 25
            self.root.update_idletasks()

            # 步骤 2: 使用 Meeko 转换 SDF 文件为 PDBQT 文件
            print("正在生成 PDBQT 文件...")
            subprocess.run([
                "python", self.prepare_ligand_script,
                "-i", sdf_file,
                "--multimol_outdir", intermediate_dir,
                "--multimol_prefix", "lig"
            ], check=True)
            print("所有配体已成功生成 PDBQT 文件。")

            # 更新进度条
            self.progress_bar['value'] = 50
            self.root.update_idletasks()

            # 步骤 3: 批量对接
            print("正在进行批量对接...")
            pdbqt_files = [f for f in os.listdir(intermediate_dir) if f.endswith(".pdbqt")]
            for ligand_pdbqt in pdbqt_files:
                ligand_path = os.path.join(intermediate_dir, ligand_pdbqt)
                output_prefix = os.path.join(intermediate_dir, os.path.splitext(ligand_pdbqt)[0])
                command = [
                    self.vina_executable,
                    "--receptor", receptor_pdbqt,
                    "--ligand", ligand_path,
                    "--config", config_file,
                    "--out", output_prefix + "_out.pdbqt"
                ]
                print("执行命令:", " ".join(command))
                subprocess.run(command, check=True)
                print(f"{ligand_pdbqt} 对接成功！")

            # 更新进度条
            self.progress_bar['value'] = 75
            self.root.update_idletasks()

            # 步骤 4: 提取对接结果
            print("正在提取对接结果...")
            molecules = []
            legends = []
            infos = []

            for pdbqt_file in os.listdir(intermediate_dir):
                if pdbqt_file.endswith("_out.pdbqt"):
                    input_pdbqt = os.path.join(intermediate_dir, pdbqt_file)
                    output_sdf = os.path.join(intermediate_dir, os.path.splitext(pdbqt_file)[0] + ".sdf")
                    
                    command = [
                        "python", self.export_script,
                        input_pdbqt,
                        "-s", output_sdf
                    ]
                    print("执行命令:", " ".join(command))
                    subprocess.run(command, check=True)
                    print(f"结果成功保存为: {output_sdf}")
                    molname = os.path.basename(output_sdf).strip('_out.sdf')
                    mol = Chem.SDMolSupplier(output_sdf)[0]
                    smiles = Chem.MolToSmiles(mol)
                    mol_2D = Chem.MolFromSmiles(smiles)
                    meeko_data = mol.GetPropsAsDict()['meeko']
                    meeko_dict = json.loads(meeko_data)
                    score = meeko_dict['free_energy']

                    # 保存分子和打分到列表
                    molecules.append(mol_2D)
                    legends.append(f"{molname}\nScore: {score}")
                    info = [molname,smiles,score]
                    infos.append(info)

            # 保存打分数据
            output_csv = os.path.join(workdir, "docking_scores.csv")
            # 打开 CSV 文件并写入标题行
            with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["MoleculeName", "SMILES", "Score"])  # 写入标题行
                for info in infos:
                    csvwriter.writerow(info)            



            print(f"分子对接打分已保存至: {output_csv}")
            # 绘制分子网格
            if molecules:
                grid_image = Draw.MolsToGridImage(
                    mols=molecules,
                    legends=legends,
                    molsPerRow=4,  # 每行显示的分子数量
                    subImgSize=(300, 300)  # 每个分子的图像大小
                )
                

                # 保存图像到文件
                output_image = os.path.join(workdir, "docking_results.png")
                grid_image.save(output_image)
                print(f"分子对接打分已保存至: {output_image}")
            else:
                print("未找到有效的分子进行绘制。")

            # 更新进度条
            self.progress_bar['value'] = 100
            self.root.update_idletasks()

            messagebox.showinfo("完成", "对接和分析完成！\n 对接结果在 "+workdir)

        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"执行过程中发生错误: {e}")



if __name__ == "__main__":
    root = Tk()
    app = DockingApp(root)
    root.mainloop()
