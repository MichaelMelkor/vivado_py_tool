#Makefile
c_file = "calcu_codefile_lines"
file_suffix = ".c"

del_vivado_jou_log:
	rm -R *.jou
	rm -R *.log

run:
	python3 run.py

open_gui_proj:
	python3 open_vivado.py
	
get_all_code_files:
	python3 get_all_code_files.py

get_all_ip_files:
	python3 get_all_ip_files.py

compile_c:
	gcc ${c_file}${file_suffix} -o ${c_file}.out
