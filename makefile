#Makefile
c_file = "calcu_codefile_lines"
c_file_suffix = ".c"

del_vivado_jou_log:
	rm -R *.jou
	rm -R *.log

run:
	python3 run.py

compile_c:
	gcc ${c_file}${c_file_suffix} -o ${c_file}.out
