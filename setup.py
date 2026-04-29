from setuptools import setup, find_packages

setup(
    name='knowsys',  # 你的项目名称
    version='1.0.4',  # 你的项目版本
    author='Chunyang Li',  # 你的名字
    author_email='lichunyang_1@outlook.com',  # 你的邮箱
    packages=find_packages(),  # 自动发现项目中的所有包
    # 你的项目描述
    description='',
    # 更详细的长的项目描述，可以放在一个单独的文件里，然后在这里引用
    # long_description=open('README.md').read(),
    # 指定项目分类
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    # 项目依赖项
    install_requires=[
        # 'requests',  # 举例，如果你的项目依赖requests库
        # 'numpy',
    ],
	package_data={
       # 任何在your_package包目录下的'.txt'文件都会被包括
       'knowsys.cached_data': ['*.csv', '*.md', '*.json'],
       # 你也可以指定子目录
       # 'your_package.subpackage': ['*.csv'],
   },
    # # 项目入口点，如果你的包是一个应用程序
    # entry_points={
    #     'console_scripts': [
    #         'your_script_name=your_package_name.your_script_file:main_function',
    #     ],
    # },
    # # 项目URL
    # url='https://github.com/your_username/your_package_name',
    # # 指定许可证
    # license='MIT',
    # # 指定关键词
    # keywords='your project keywords',
    # 指定项目依赖的其他Python包
    # project.includes=['package1', 'package2'],
    # 如果你的包需要额外的编译或链接参数，可以在这里指定
    # project.ext_modules=[...],
)
