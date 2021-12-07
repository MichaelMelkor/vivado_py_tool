#define BUFF_SIZE 1000
#define COMM_KEYWORD_MAXSIZE 5

#include<stdio.h>
#include<string.h>
#include<stdbool.h>

typedef struct{
    char str[COMM_KEYWORD_MAXSIZE];
    int len;
} comm_keyword;

typedef struct{
    char buff[BUFF_SIZE];

    comm_keyword line_comm_keyword;
    comm_keyword block_comm_beginword;
    comm_keyword block_comm_endword;

    bool empty_line_flag;
    bool code_line_flag;
    bool line_comm_flag;
    bool block_comm_flag;
    bool block_comm_ing_flag;
} code_file_line;

typedef struct{
    FILE *fp;

    char line_comm_keyword[COMM_KEYWORD_MAXSIZE];
    char block_comm_beginword[COMM_KEYWORD_MAXSIZE];
    char block_comm_endword[COMM_KEYWORD_MAXSIZE];

    int empty_line_num;
    int code_line_num;
    int line_comm_line_num;
    int block_comm_line_num;
    int all_line_num;
} code_file;

char getLineText(FILE *fp, char *buff)
{
    int  buff_index = 0;
    char fscanf_rov = ' ';
    while(1)
    {
        fscanf_rov = fscanf(fp,"%c", buff+buff_index);
        if(fscanf_rov == EOF)
            break;
        buff_index += 1;
        if(buff[buff_index-1] == '\n')
            break;
        else if(buff_index == BUFF_SIZE)
            break;
    }
    buff[buff_index] = '\0';
    return fscanf_rov;
}

bool copyStringPart(char *new_string, char *src_string, int start_index, int str_len)
{
    int i = 0;
    if(start_index >= 0 && str_len > 0 && start_index + str_len < sizeof(src_string) && str_len < sizeof(new_string))
    {
        for(i=0;i<str_len;i++)
        {
            new_string[i] = src_string[start_index+i];
        }
        new_string[i] = '\0';
        return true;
    }
    else
    {
        new_string[i] = '\0';
        return false;
    }
}

bool judgeEmptyChar(char ch)
{
    switch (ch)
    {
    case '\t':
        return true;
    case '\n':
        return true;
    case '\v':
        return true;
    case '\r':
        return true;
    case '\f':
        return true;
    case '\0':
        return true;
    case ' ':
        return true;
    default:
        return false;
    }
}

int judgeEmptyLine(char *buff, int buff_len)
{
    int buff_index = 0;
    for(buff_index=0;buff_index<buff_len;buff_index++)
    {
        if(buff_index == BUFF_SIZE - 1)
            break;
        else if(judgeEmptyChar(buff[buff_index]))
            continue;
        else
            return buff_index;
    }
    return -1;
}

//计算字符串长度，还是使用标准库string.h里的strlen吧
//int getStringLength(char *string)
//{
//    int str_index = 0;
//    int string_num = sizeof(string) / sizeof(string[0]);
//    for(str_index=0;string[str_index]!='\0' || str_index<string_num;str_index++);
//    return str_index;
//}

int findKeywordLocInStr(char *keyword, char *string, int start_index)
{
    int str_index = 0;
    int key_index = 0;
    int str_length = 0;
    int key_length = 0;
    //获取关键词以及所查找字符串的长度
    str_length = strlen(string);
    key_length = strlen(keyword);
    //判断异常情况
    if(key_length < str_length)
    {
        if(start_index + key_length <= str_length)
            str_index = start_index;
        else
            return -1;
    }
    else 
        return -1;
    //在字符串中查找关键词
    for(str_index=0;string[str_index]!='\0';str_index++)
    {
        for(key_index=0;keyword[key_index]!='\0' && string[str_index+key_index]==keyword[key_index];key_index++);
        if(keyword[key_index] == '\0')
            return str_index;
    }
    return -1;
}

int checkLineCode(code_file_line *cfl_ptr)
{
    //printf("%s\n",cfl_ptr->buff);
    //当前代码行的字符串索引值，首先初始化为当前行中第一个非空字符所在的位置
    int buff_index = judgeEmptyLine(cfl_ptr->buff, strlen(cfl_ptr->buff));
    char buff_char;
    int tmp_index;
    char tmp_str[COMM_KEYWORD_MAXSIZE];
    //printf(">>buff_index : %d\n", buff_index);
    //初始化部分参数标志
    cfl_ptr->code_line_flag = false;
    cfl_ptr->line_comm_flag = false;
    if(cfl_ptr->block_comm_ing_flag == false)
        cfl_ptr->block_comm_flag = false;

    if(buff_index == -1)//当前行是空行
    {
        cfl_ptr->empty_line_flag = true;
        cfl_ptr->code_line_flag  = false;
        cfl_ptr->line_comm_flag  = false;
    }
    else//当前行不是空行
    {
        cfl_ptr->empty_line_flag = false;
        while(1)
        {
            buff_char = cfl_ptr->buff[buff_index];
            if(buff_char == '\n' || buff_char == '\0')
                break;
            else
            {
                if(cfl_ptr->block_comm_ing_flag)//若目前仍处在块注释内，首先查找块注释结束符
                {
                    tmp_index = findKeywordLocInStr(cfl_ptr->block_comm_endword.str, cfl_ptr->buff, buff_index);
                    if(tmp_index == -1)//当前行中，未找到块注释结束符
                    {
                        cfl_ptr->code_line_flag = false;
                        cfl_ptr->line_comm_flag = false;
                        cfl_ptr->block_comm_flag = true;
                        cfl_ptr->block_comm_ing_flag = true;
                        break;
                    }
                    else//找到块注释结束符
                    {
                        cfl_ptr->block_comm_flag = true;
                        cfl_ptr->block_comm_ing_flag = false;
                        buff_index = tmp_index + cfl_ptr->block_comm_endword.len;
                        continue;
                    }
                }
                else//目前不在块注释内
                {
                    if(buff_char == cfl_ptr->line_comm_keyword.str[0])
                    {
                        copyStringPart(tmp_str, cfl_ptr->buff, buff_index, cfl_ptr->line_comm_keyword.len);
                        if(strcmp(tmp_str, cfl_ptr->line_comm_keyword.str) == 0)//在当前位置检测到行注释符
                        {
                            cfl_ptr->line_comm_flag = true;
                            cfl_ptr->block_comm_ing_flag = false;
                            break;
                        }
                    }

                    if(buff_char == cfl_ptr->block_comm_beginword.str[0])
                    {
                        copyStringPart(tmp_str, cfl_ptr->buff, buff_index, cfl_ptr->block_comm_beginword.len);
                        if(strcmp(tmp_str, cfl_ptr->block_comm_beginword.str) == 0)//在当前位置检测到块注释起始符
                        {
                            cfl_ptr->block_comm_flag = true;
                            cfl_ptr->block_comm_ing_flag = true;
                            buff_index += cfl_ptr->block_comm_beginword.len;
                            continue;
                        }
                    }
                    cfl_ptr->code_line_flag = true;
                    buff_index += 1;
                }
            }
        }
    }
    return 0;
}

int countAllCodeLines(code_file *file_ptr)
{
    char getLineText_rov;

    //初始化代码文件各个行数变量
    file_ptr->empty_line_num = 0;
    file_ptr->code_line_num = 0;
    file_ptr->line_comm_line_num = 0;
    file_ptr->block_comm_line_num = 0;
    file_ptr->all_line_num = 0;

    //定义代码行结构体并初始化
    code_file_line cfl;

    cfl.empty_line_flag = false;
    cfl.code_line_flag = false;
    cfl.line_comm_flag = false;
    cfl.block_comm_flag = false;
    cfl.block_comm_ing_flag = false;

    strcpy(cfl.line_comm_keyword.str, file_ptr->line_comm_keyword);
    cfl.line_comm_keyword.len = strlen(file_ptr->line_comm_keyword);
    strcpy(cfl.block_comm_beginword.str, file_ptr->block_comm_beginword);
    cfl.block_comm_beginword.len = strlen(file_ptr->block_comm_beginword);
    strcpy(cfl.block_comm_endword.str, file_ptr->block_comm_endword);
    cfl.block_comm_endword.len = strlen(file_ptr->block_comm_endword);
    

    while(1)
    {
        getLineText_rov = getLineText(file_ptr->fp, cfl.buff);
        checkLineCode(&cfl);
        //判断代码行检测后的结果，并根据结果控制各行数变量进行赋值
        if(cfl.empty_line_flag)
        {
            file_ptr->empty_line_num += 1;
            //printf("empty line : %d\n", file_ptr->all_line_num+1);
        }
        if(cfl.code_line_flag)
        {
            file_ptr->code_line_num += 1;
            //printf("code line : %d\n", file_ptr->all_line_num+1);
        }
        if(cfl.line_comm_flag)
        {
            file_ptr->line_comm_line_num += 1;
            //printf("line comm line : %d\n", file_ptr->all_line_num+1);
        }
        if(cfl.block_comm_flag)
        {
            file_ptr->block_comm_line_num += 1;
            //printf("block comm line : %d\n", file_ptr->all_line_num+1);
        }
        file_ptr->all_line_num += 1;
        if(getLineText_rov == EOF)
            break;
    }
    return 0;
}

int countCodeFileLines(char *CodeFileName, char *WrFileName)
{
    FILE *WrFp;
    code_file File;
    int CodeFileNameLen = 0;
    int WrFileNameLen = 0;
    int i = 0;
    File.fp = fopen(CodeFileName, "r");
    WrFp = fopen(WrFileName, "a");
    if(File.fp == NULL)
    {
        CodeFileNameLen = strlen(CodeFileName);
        printf("[Error] File ");
        for(i=0;i<CodeFileNameLen;i++)
        {
            printf("%c", CodeFileName[i]);
        }
        printf(" is not exist!\n");
    }
    else if(WrFp == NULL)
    {
        WrFileNameLen = strlen(WrFileName);
        printf("[Error] File ");
        for(i=0;i<WrFileNameLen;i++)
        {
            printf("%c", WrFileName[i]);
        }
        printf(" is not exist!\n");
    }
    else
    {
        strcpy(File.line_comm_keyword, "//\0");
        strcpy(File.block_comm_beginword, "/*\0");
        strcpy(File.block_comm_endword, "*/\0");
        countAllCodeLines(&File);
        fprintf(WrFp, "/***********************************************************/\n");
        fprintf(WrFp, ">> File's path is ");
        CodeFileNameLen = strlen(CodeFileName);
        for(i=0;i<CodeFileNameLen;i++)
        {
            fprintf(WrFp, "%c", CodeFileName[i]);
        }
        fprintf(WrFp, "\n");
        fprintf(WrFp, "## empty lines num : %d\n", File.empty_line_num);
        fprintf(WrFp, "## code lines num : %d\n", File.code_line_num);
        fprintf(WrFp, "## line comment lines num : %d\n", File.line_comm_line_num);
        fprintf(WrFp, "## block comment lines num : %d\n", File.block_comm_line_num);
        fprintf(WrFp, "## all lines num : %d\n", File.all_line_num);
        fclose(File.fp);
        fclose(WrFp);
    }
    return 0;
}

int main(int argc, char *argv[])
{
    FILE *fp;
    code_file file;
    char line_text[BUFF_SIZE];
    char getLineText_rov;
    int  FindTestLoc;
    int  i;
    char a[] = "abcdefg\0";
    char b[] = "bc\0";
    char c[] = "ba\0";
    //fp = fopen("./1.v", "r");
    //char CodeFileName[] = "./1.v\0";
    char WrFileName[200] = "\0";
    int WrFileNameLen = 0;
    if(argc > 2)
    {
        WrFileNameLen = strlen(argv[1]);
        for(i=0;i<WrFileNameLen;i++)
            WrFileName[i] = argv[1][i];
        for(i=2;i<argc;i++)
            countCodeFileLines(argv[i], WrFileName);
    }
    else
        printf("There is no file to count!\n");

    //*************************
    //测试getLineText和judgeEmptyLine函数
    //*************************
    //while(1)
    //{
    //    getLineText_rov = getLineText(fp, line_text);
    //    printf("%s", line_text);
    //    printf("******* %d *******\n", judgeEmptyLine(line_text, strlen(line_text)));
    //    if(getLineText_rov == EOF) break;
    //}

    //*************************
    //测试findKeywordLocInStr函数
    //*************************
    //FindTestLoc = findKeywordLocInStr(b,a,10);
    //printf("%d\n", FindTestLoc);
    //FindTestLoc = findKeywordLocInStr(c,a,1);
    //printf("%d\n", FindTestLoc);
    //FindTestLoc = findKeywordLocInStr(a,b,3);
    //printf("%d\n", FindTestLoc);

    //*************************
    //测试checkLineCode函数
    //*************************
    //code_file_line cfl;
    //strcpy(cfl.buff, "abcdefghijklmnop\0");
    //checkLineCode(&cfl);
    
    //*************************
    //测试countAllCodeLines函数
    //*************************
    //file.fp = fp;
    //strcpy(file.line_comm_keyword, "//\0");
    //strcpy(file.block_comm_beginword, "/*\0");
    //strcpy(file.block_comm_endword, "*/\0");
    //countAllCodeLines(&file);
    //printf("empty lines num : %d\n", file.empty_line_num);
    //printf("code lines num : %d\n", file.code_line_num);
    //printf("line comment lines num : %d\n", file.line_comm_line_num);
    //printf("block comment lines num : %d\n", file.block_comm_line_num);
    //printf("all lines num : %d\n", file.all_line_num);

    //fclose(fp);
    return 0;
}
