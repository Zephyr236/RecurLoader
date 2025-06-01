import random
import string

def generate_c_junk_code(num_fragments=10):
    # 生成随机标识符
    def rand_id():
        return ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
    
    # 生成随机整数值
    def rand_int():
        return str(random.randint(1, 10000))
    
    # 生成随机浮点值
    def rand_float():
        return f"{random.uniform(0.1, 100.0):.4f}"
    
    # 生成随机字符串值
    def rand_str():
        return '"' + ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 15))) + '"'
    
    # 完整独立的模板列表
    templates = [
        # 变量声明和打印
        "\tint {v1} = {i1}; printf(\"%d\", {v1});",
        "\tfloat {v1} = {f1}f; printf(\"%f\", {v1});",
        "\tchar* {v1} = {s1}; printf(\"%s\", {v1});",
        "\tdouble {v1} = {f1}; printf(\"%.2f\", {v1});",
        
        # 多变量操作
        "\tint {v1} = {i1}; int {v2} = {i2}; {v1} = {v1} * {v2}; printf(\"%d\", {v1});",
        "\tfloat {v1} = {f1}; float {v2} = {f2}; {v1} = {v1} + {v2}; printf(\"%f\", {v1});",
        "\tchar* {v1} = {s1}; char* {v2} = {s2}; printf(\"%s%s\", {v1}, {v2});",
        
        # 简单循环
        "\tfor(int {v1} = 0; {v1} < {i1}; {v1}++) { printf(\"%d \", {v1}); }",
        "\tint {v1} = 0; while({v1} < {i1}) { printf(\"%d \", {v1}); {v1}++; }",
        
        # 条件语句
        "\tint {v1} = {i1}; if({v1} > 1000) { printf(\"Big number: %d\", {v1}); }",
        "\tfloat {v1} = {f1}; if({v1} < 10.0) { printf(\"Small float: %f\", {v1}); }",
        
        # 数组操作
        "\tint {v1}[5] = {1, 2, 3, 4, 5}; for(int i=0; i<5; i++) printf(\"%d \", {v1}[i]);",
        "\tchar* {v1}[3] = {\"a\", \"b\", \"c\"}; for(int i=0; i<3; i++) printf(\"%s \", {v1}[i]);",
        
        
        # 类型转换
        "\tfloat {v1} = {f1}; int {v2} = (int){v1}; printf(\"Original: %f, Converted: %d\", {v1}, {v2});",
        "\tint {v1} = {i1}; float {v2} = (float){v1}; printf(\"Original: %d, Converted: %f\", {v1}, {v2});",
    
        "\tDWORD {v1} = GetTickCount(); printf(\"System uptime: %lu ms\\n\", {v1});",
        "\tchar {v1}[MAX_PATH]; GetModuleFileNameA(NULL, {v1}, MAX_PATH); printf(\"Module path: %s\\n\", {v1});",
        "\tSYSTEMTIME {v1}; GetLocalTime(&{v1}); printf(\"Current date: %04d-%02d-%02d\\n\", {v1}.wYear, {v1}.wMonth, {v1}.wDay);",
        "\tHANDLE {v1} = GetCurrentProcess(); printf(\"Process handle: %p\\n\", {v1});",
        "\tPOINT {v1}; GetCursorPos(&{v1}); printf(\"Cursor position: %d, %d\\n\", {v1}.x, {v1}.y);",
        "\tunsigned long {v1} = GetLastError(); printf(\"Last error code: %lu\\n\", {v1});",
        "\tchar {v1}[256]; DWORD size{v1} = sizeof({v1}); GetComputerNameA({v1}, &size{v1}); printf(\"Computer name: %s\\n\", {v1});",

        "\ttime_t {v1} = time(NULL); printf(\"Current time: %ld\\n\", {v1});",
        "\tclock_t {v1} = clock(); printf(\"Processor time: %ld\\n\", {v1});",
        "\tUUID {v1}; UuidCreate(&{v1}); printf(\"Generated GUID\\n\");",
        "\tchar {v1}[256]; DWORD len{v1} = sizeof({v1}); GetUserNameA({v1}, &len{v1}); printf(\"Current user: %s\\n\", {v1});",

        "\tdouble {v1} = sin({f1}); printf(\"Sine: %f\\n\", {v1});",
        "\tint {v1} = abs({i1}); printf(\"Absolute value: %d\\n\", {v1});",
        "\tdouble {v1} = sqrt({f1}); printf(\"Square root: %f\\n\", {v1});",
        "\tCRITICAL_SECTION cs{v1}; InitializeCriticalSection(&cs{v1}); DeleteCriticalSection(&cs{v1});",
    ]
    
    # 结果列表
    fragments = []
    
    for _ in range(num_fragments):
        
        # 选择随机模板
        tpl = random.choice(templates)
        
        # 替换占位符
        # 首先处理变量
        while '{v1}' in tpl:
            tpl = tpl.replace('{v1}', rand_id())
        while '{v2}' in tpl:
            tpl = tpl.replace('{v2}', rand_id())
        
        # 然后处理数值
        while '{i1}' in tpl:
            tpl = tpl.replace('{i1}', rand_int())
        while '{i2}' in tpl:
            tpl = tpl.replace('{i2}', rand_int())
            
        while '{f1}' in tpl:
            tpl = tpl.replace('{f1}', rand_float())
        while '{f2}' in tpl:
            tpl = tpl.replace('{f2}', rand_float())
            
        while '{s1}' in tpl:
            tpl = tpl.replace('{s1}', rand_str())
        while '{s2}' in tpl:
            tpl = tpl.replace('{s2}', rand_str())
        
        fragments.append(tpl)
    
    return '\n'.join(fragments)

# 示例用法
if __name__ == "__main__":
    print(generate_c_junk_code(2))