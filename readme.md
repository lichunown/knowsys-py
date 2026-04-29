# knowsys-py

`knowsys-py` 是一个用于加载“城市知识体系”离线数据的 Python 包。项目把包内 `cached_data` 目录中的 CSV 数据读入内存，并组织成一套可查询、可遍历、可导出的树/图结构。

当前代码的核心入口是 `knowsys.loader_from_files`：导入包时会自动读取数据文件，构建一个全局 `TreeSpace` 对象，并通过 `knowsys.knowsys` 暴露出来。

## 环境要求

- Python >= 3.10
- pandas >= 1.5

本地开发安装：

```powershell
pip install -e .
```

如果只是直接在当前仓库里运行示例，也可以不安装，确保命令在项目根目录执行即可。

## 快速开始

```python
import knowsys

space = knowsys.knowsys

print(space.root)           # TreeNode(知识体系)
print(space.entity_root)    # Entity(实体)
print(space.relation_root)  # Relation(关系)

person = space.get_by_name("人")
print(person.terms[:5])              # 人对应的实体术语
print(person.attributes[:5])         # 人的一级属性
print(person.this_to_relation_terms[:5])  # 以“人”为起点的关系术语

nodes, edges = space.export(is_hetero=True)
print(len(nodes), len(edges))
```

在 Windows 终端中如果看到中文乱码，可以先设置：

```powershell
$env:PYTHONIOENCODING = "utf-8"
```

## 项目结构

```text
knowsys-py/
├─ setup.py
├─ readme.md
└─ knowsys/
   ├─ __init__.py
   ├─ enums.py
   ├─ loader_from_files.py
   ├─ knowsys_utils/
   │  ├─ file_utils.py
   │  └─ strings.py
   ├─ cached_data/
   │  ├─ knowsys.json
   │  └─ knowsys_table_*.csv
   ├─ tree/
   │  ├─ node.py
   │  ├─ node_list.py
   │  ├─ space.py
   │  ├─ cacheing.py
   │  └─ utils.py
   └─ types/
      ├─ entity.py
      ├─ relation.py
      ├─ attribute.py
      ├─ entity_term.py
      ├─ relation_term.py
      ├─ er_term.py
      └─ attribute_term.py
```

## 核心概念

### TreeSpace

`TreeSpace` 是整个知识体系的内存容器，内部维护：

- `node_dict`：按节点 id 保存所有节点；
- 名称索引、父子索引、类型索引；
- 属性、术语、关系术语、实体术语、实体关系术语等反向索引；
- `export()` 图导出能力。

常用入口：

```python
space.root                 # 知识体系根节点
space.entity_root          # 实体分类根节点
space.relation_root        # 关系分类根节点
space.entity_term_root     # 实体术语根节点
space.relation_term_root   # 关系术语根节点
space.er_term_root         # 实体关系术语根节点
space.attribute_root       # 属性根节点
space.attribute_term_root  # 属性术语根节点
```

### TreeNode

`TreeNode` 是所有节点类型的基类，提供：

- `id_`、`name`、`parent_id`、`space`；
- `parent`、`children`、`brothers`、`level`、`depth`；
- `print_tree()` 树形打印；
- `export()` 导出自身节点和父子边；
- 延迟校验与继承字段机制。

如果创建节点时父节点尚未加载，`TreeNode` 会把校验逻辑放入 `_lazy_check_funcs`，最后由 `space.lazy_check()` 统一处理。

### NodeList

`NodeList` 继承自 `list`，用于查询结果集合，额外提供：

- `filter(func)`
- `get_by_name(name)`
- `get_by_name_all(name)`
- `sample()`
- `sample_k(k)`
- `sample_with_children()`

## 业务节点类型

| 类型 | 含义 | 主要关联 |
| --- | --- | --- |
| `Entity` | 实体分类，如人、地、事、物、组织 | 实体术语、属性、可用关系术语 |
| `Relation` | 关系分类，如人-地、人-事 | 起点实体、终点实体、方向类型、关系术语 |
| `Attribute` | 属性，如姓名、出生日期、经纬度 | 被哪个实体或关系修饰、属性术语 |
| `EntityTerm` | 实体术语，如城市居民 | 归属实体分类 |
| `RelationTerm` | 关系术语，如人常驻地 | 归属关系分类、方向、可用实体关系术语 |
| `ERTerm` | 实体关系术语/陈述术语 | 关联关系术语，当前普通陈述的实体术语字段为空 |
| `AttributeTerm` | 属性术语/属性表达 | 归属属性、修饰对象 |

方向相关枚举定义在 `knowsys.enums`：

- `DirectionType.UNKNOWN`
- `DirectionType.BiDirection`
- `DirectionType.Direction`
- `Direction.Forward`
- `Direction.Backward`
- `Direction.BiDirection`

## 数据加载流程

`loader_from_files.py` 在导入时按固定顺序构建知识体系：

1. 创建 `TreeSpace("Knowsys")`。
2. 创建硬编码根节点：
   - `知识体系`
   - `实体`
   - `关系`
3. 读取 `knowsys_table_ks_system_category.csv`：
   - 仅保留 `del_stat == 0` 的记录；
   - 跳过前 3 行根分类；
   - `category_full_name_cn` 以 `实体` 开头的记录生成 `Entity`；
   - `category_full_name_cn` 以 `关系` 开头的记录生成 `Relation`，并从类似 `关系/人-地` 的路径中解析起点实体和终点实体。
4. 读取 `knowsys_table_ks_system_direction.csv`：
   - 创建 `关系术语` 根节点；
   - 根据 `directed`、`reversed` 设置关系方向；
   - 生成 `RelationTerm`。
5. 读取 `knowsys_table_ks_system_entity.csv`：
   - 仅加载 `version_name == "standard"` 且 `del_stat == 0` 的记录；
   - 创建 `实体术语` 根节点；
   - 使用 `entity_term_mappings` 把历史实体术语分类映射到当前实体分类；
   - 生成 `EntityTerm`。
6. 读取 `knowsys_table_ks_system_category_statement.csv`：
   - 创建 `实体关系术语` 根节点；
   - 生成 `ERTerm`；
   - 当前普通陈述只绑定 `relation_term_id`，`entity_term_id` 传入 `None`。
7. 读取 `knowsys_table_ks_system_property.csv`：
   - 创建 `属性`、`实体属性`、`关系属性` 根节点；
   - 根据 `category_code` 查找被修饰对象；
   - 生成 `Attribute`。当前属性都挂在 `实体属性` 下。
8. 读取 `knowsys_table_ks_system_property_expression.csv`：
   - 创建 `属性术语` 根节点；
   - 根据 `property_code` 查找属性，根据 `category_code` 查找修饰对象；
   - 生成 `AttributeTerm`。
9. 调用 `space.lazy_check()`：
   - 执行延迟父节点校验；
   - 继承 `Relation`、`Attribute`、`EntityTerm`、`RelationTerm`、`ERTerm`、`AttributeTerm` 中声明的 `__inherited_properties__`；
   - 重建查询索引。

## 当前主加载器使用的数据表

| 文件 | 用途 |
| --- | --- |
| `knowsys_table_ks_system_category.csv` | 加载实体分类和关系分类 |
| `knowsys_table_ks_system_direction.csv` | 加载关系方向和关系术语 |
| `knowsys_table_ks_system_entity.csv` | 加载实体术语 |
| `knowsys_table_ks_system_category_statement.csv` | 加载实体关系术语/陈述术语 |
| `knowsys_table_ks_system_property.csv` | 加载属性 |
| `knowsys_table_ks_system_property_expression.csv` | 加载属性术语 |

`cached_data` 中还包含 case、statement_expand、direction_text、property_prod、tag、原始 `knowsys.json` 等文件；这些文件当前没有被 `loader_from_files.py` 主流程直接读取。

## 查询示例

按名称查找：

```python
person = space.get_by_name("人")
all_person_named_nodes = space.get_by_name_all("人")
```

查看实体的术语和属性：

```python
person = space.get_by_name("人")

person.terms          # 直接挂在实体术语根下的术语
person.terms_all      # 该实体的全部术语
person.attributes     # 一级属性
person.attributes_all # 全部属性
person.attributes_terms_all
```

查看关系和关系术语：

```python
relation = space.get_by_name("人-地")

relation.from_entity
relation.to_entity
relation.direction_type
relation.terms
relation.terms_all
```

查看某个实体可用的关系术语：

```python
person = space.get_by_name("人")

person.this_to_relation_terms    # 以该实体为起点
person.this_from_relation_terms  # 以该实体为终点
person.enable_er_terms           # 起点方向可用的实体关系术语
person.enable_er_terms_backward  # 终点方向可用的实体关系术语
```

导出图结构：

```python
nodes, edges = space.export(is_hetero=True)

# nodes: [(node_id, node_type, node_name), ...]
# edges: [(source_id, edge_type, target_id), ...]
```

当 `is_hetero=True` 时，导出边会区分语义类型，例如：

- `contains`
- `e_r`
- `r_e`
- `e_r_unknown`
- `r_e_unknown`
- `term_to_entity`
- `belong_to_relation`
- `conn_entity_term`
- `conn_relation_term`
- `modify`
- `belong_to_attr`

当 `is_hetero=False` 时，节点类型统一为 `knowsys_node`，边类型统一为 `knowsys_edge`。

## 已验证的数据规模

在当前仓库数据上执行导入后，统计结果为：

| 类型 | 数量 |
| --- | ---: |
| 全部节点 | 4081 |
| `TreeNode` | 1 |
| `Entity` | 6 |
| `Relation` | 119 |
| `EntityTerm` | 165 |
| `RelationTerm` | 177 |
| `ERTerm` | 844 |
| `Attribute` | 1048 |
| `AttributeTerm` | 1721 |
| 异构图导出边 | 10861 |

主要根节点包括：

```text
知识体系
关系术语
实体术语
实体关系术语
属性
属性术语
```

## 开发说明

- `knowsys.__init__` 会导入 `loader_from_files.space as knowsys`，因此 `import knowsys` 会立即加载全部缓存数据。
- `TreeSpace` 维护多组索引，适合读多写少的场景。节点删除或延迟校验后会调用 `rebuild_indexes()` 重建索引。
- `cacheing.py` 定义了一个外部缓存包装器和 mixin，但当前主加载流程没有使用它。
- `(tmp) parse_json.py` 是历史转换脚本，用于把 `knowsys.json` 中的 table 数据导出为 CSV。当前工作区版本从 `knowsys_utils.file_utils` 导入 `load_json`，但它不属于主运行路径；如果单独执行，需要确认运行目录或 `PYTHONPATH` 能找到 `knowsys_utils`。
- `knowsys_utils` 提供 JSON、文本、pickle、MD5 和随机字符串等通用工具。主加载器没有使用它；其中 `file_utils.py` 额外导入了 `numpy` 和 `torch`，因此不建议把它视为主包的必需依赖。
- `category_map` 和 `entity_term_mappings` 是历史数据兼容映射，修改数据版本时需要同步检查。

## 常见问题

### 为什么导入包就会加载数据？

这是当前设计：`knowsys/__init__.py` 直接导入 `loader_from_files` 中已经构建好的 `space`。这样使用简单，但也意味着首次导入会读取 CSV 并构建全部索引。

### 为什么 CSV 里有一个空列名？

部分 CSV 是从 pandas 导出时保留了默认索引列，因此第一列没有业务字段名。主加载器没有依赖这列。

### 查不到节点时会发生什么？

`space.get_by_name(name)` 找不到时返回 `None`；但 `NodeList.get_by_name(name)` 假设一定存在，找不到会抛出索引错误。业务代码里如果节点名不确定，建议优先使用 `get_by_name_all()` 或先判断返回值。

### 数据加载时会忽略哪些记录？

主流程会忽略：

- `del_stat != 0` 的记录；
- 实体术语表中 `version_name != "standard"` 的记录；
- 属性或属性术语中找不到修饰对象、属性对象的记录。
