import os

def consolidate_project(output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py') or file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(f'--- {file_path} ---\n\n')
                        outfile.write(infile.read())
                        outfile.write('\n\n')

if __name__ == '__main__':
    output_file = 'consolidated_project.txt'
    consolidate_project(output_file)
    print(f'Projeto consolidado em {output_file}')
