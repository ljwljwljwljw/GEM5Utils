from par import *
from checkpoint import *
import time
import argparse


gem5_args = """{gem5_path}/build/RISCV/gem5.opt
--outdir={out_dir}
{gem5_path}/configs/example/fs.py
--xiangshan-system
--enable-difftest
--difftest-ref-so=./gem5_run/riscv64-nemu-interpreter-so
--generic-rv-cpt={cpt_path}
--mem-type=DDR4_2400_16x4
--cpu-type=DerivO3CPU
--bp-type=LTAGE
--caches
--cacheline_size=64
--l1i_size=128kB
--l1i_assoc=8
--l1d_size=128kB
--l1d_assoc=8
--l2cache
--l2_size=1MB
--l2_assoc=8
--l2-hwp-type=SMSPrefetcher
--l3cache
--l3_size=2MB
--l3_assoc=8
--mem-size=8GB
--num-cpus=1
-I=40000000
--warmup-insts-no-switch=20000000"""

"""--dramsim3-ini={gem5_path}/xiangshan_DDR4_8Gb_x8_2400.ini"""


def gen_gem5_tasks(cpt_dir, gem5_path, result_dir):
    cpts = get_checkpoints(cpt_dir)
    tasks = []
    for c in cpts:
        cpt_path = c.get_path()
        out_dir = c.output_dir("./gem5_run/results/")
        cmd = gem5_args.format(
          out_dir=out_dir,
          gem5_path=gem5_path,
          cpt_path=cpt_path).replace("\n", " ")
        #print(cmd)
        task = Task(cmd, out_dir)
        tasks.append(task)
    return tasks


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--jobs', default=112)
    parser.add_argument('--cpt-dir',
                        default="/nfs-nvme/home/share/checkpoints_profiles/spec06_rv64gcb_o2_20m")
    parser.add_argument('--gem5', default='../GEM5_nfs', help="Path for GEM5")
    t = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    parser.add_argument('--result-dir', default=t, help="Result output dir")
    args = parser.parse_args()
    tasks = gen_gem5_tasks(args.cpt_dir, args.gem5, args.result_dir)
    run({
        "num_workers": args.jobs,
        "tasks": tasks
    })
