import os
import json
from py2neo import Graph,Node

class MedicalGraph:
    def __init__(self):
        """
        加载数据文件，连接neo4j
        """
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/medical.json')
        self.g = Graph(
            host="10.112.57.93",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="neo4j123")

    '''读取文件， 获得实体，关系，属性列表'''
    def read_nodes(self):
        # 实体列表
        departments = []  # 科室
        checks = []  # 检查项目
        diseases = []  # 疾病
        symptoms = []  # 疾病症状
        drugs = []  # 药品
        producers = []  # 在售药品
        foods = []  # 食物

        disease_infos = []  # 疾病信息，这个不是实体，指实体“疾病”的属性

        # 关系列表
        rels_department = []  # 疾病－科室关系
        rels_category = []  # 疾病-具体治疗科室之间的关系 文档中未提及
        rels_check = []  # 疾病－检查关系
        rels_acompany = []  # 疾病并发关系
        rels_symptom = []  # 疾病症状关系
        rels_commonddrug = [] # 疾病－通用药品关系
        rels_recommanddrug = [] # 疾病－热门药品关系
        rels_drug_producer = []  # 厂商－药物关系 与文档中不一致
        rels_doeat = []  # 疾病－宜吃食物关系
        rels_noteat = [] # 疾病－忌吃食物关系
        rels_recommandeat = [] # 疾病－推荐吃食物关系

        count = 0
        # 遍历json文件中每一条疾病记录，将其中的信息更新到实体，关系列表中，
        # 建立一个字典disease_dict存储该疾病的各属性信息，最后将添加到disease_infos列表中
        for data in open(self.data_path, encoding='UTF-8'):
            disease_dict = {}
            count += 1
            print(count)
            data_json = json.loads(data)  # 把字符串data通过json.loads转为字典
            disease = data_json['name']  # 疾病名称
            disease_dict['name'] = disease
            diseases.append(disease)  # 该疾病名称添加到“疾病”实体列表diseases中
            disease_dict['desc'] = ''  # 疾病简介
            disease_dict['cause'] = ''  # 病因
            disease_dict['prevent'] = ''  # 预防措施
            disease_dict['cure_lasttime'] = ''  # 治疗周期
            disease_dict['cure_way'] = ''  # 治疗方式
            disease_dict['cured_prob'] = ''  # 治愈概率
            disease_dict['easy_get'] = ''  # 易感人群

            disease_dict['cure_department'] = ''  # 疾病治疗科室 文档中未提及
            disease_dict['symptom'] = ''  # 疾病症状 文档中未提及

            # 将该条疾病记录信息添加到对应实体，关系，列表中，如果疾病属性存在，设置字典中相应的值
            if 'symptom' in data_json:  # 这条疾病记录的字典的键中是否有symptom
                symptoms += data_json['symptom']  # 该疾病的症状添加到“症状”实体列表symptoms中
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])  # 将”该疾病与-该疾病症状“之间关系添加到关系列表rels_symptom中

            if 'acompany' in data_json:
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease, acompany])  # 将”该疾病-并发疾病“之间关系添加到关系列表rels_acompany中

            if 'desc' in data_json:
                disease_dict['desc'] = data_json['desc']  # 设置该疾病简介内容

            if 'prevent' in data_json:
                disease_dict['prevent'] = data_json['prevent']  # 设置该疾病预防措施

            if 'cause' in data_json:
                disease_dict['cause'] = data_json['cause']  # 设置该疾病病因

            if 'get_prob' in data_json:
                disease_dict['get_prob'] = data_json['get_prob']  # 设置该疾病治愈概率

            if 'easy_get' in data_json:
                disease_dict['easy_get'] = data_json['easy_get']  # 设置该疾病易感人群

            if 'cure_department' in data_json:
                cure_department = data_json['cure_department']  # 设置该疾病治疗科室
                if len(cure_department) == 1:
                     rels_category.append([disease, cure_department[0]])  # 将”疾病-具体治疗科室“关系添加到关系列表rels_category中
                if len(cure_department) == 2:
                    big = cure_department[0]
                    small = cure_department[1]
                    rels_department.append([small, big])  # 将”疾病-治疗科室“关系添加到关系列表rels_department中
                    rels_category.append([disease, small])  # 将”疾病-具体治疗科室“关系添加到关系列表rels_category中

                disease_dict['cure_department'] = cure_department  # 设置该疾病“科室”属性
                departments += cure_department  # 将该科室添加到科室列表中

            if 'cure_way' in data_json:
                disease_dict['cure_way'] = data_json['cure_way']  # 设置该疾病治疗方式

            if  'cure_lasttime' in data_json:
                disease_dict['cure_lasttime'] = data_json['cure_lasttime']  # 设置该疾病治疗周期

            if 'cured_prob' in data_json:
                disease_dict['cured_prob'] = data_json['cured_prob']  # 设置该疾病治愈概率

            if 'common_drug' in data_json:
                common_drug = data_json['common_drug']  # 设置该疾病通用药品属性
                for drug in common_drug:
                    rels_commonddrug.append([disease, drug])  #　更新“疾病－通用药品”关系列表rels_commonddrug
                drugs += common_drug  # 将该通用药品添加到“药品”实体列表drugs中

            if 'recommand_drug' in data_json:
                recommand_drug = data_json['recommand_drug']  # 设置该疾病热门药品属性
                drugs += recommand_drug
                for drug in recommand_drug:
                    rels_recommanddrug.append([disease, drug])

            if 'not_eat' in data_json:
                not_eat = data_json['not_eat']  # 设置该疾病禁忌食品
                for _not in not_eat:
                    rels_noteat.append([disease, _not])  # 将”疾病-禁忌食品“关系添加到关系列表中
                foods += not_eat  # 更新”食品“实体列表foods

                do_eat = data_json['do_eat']
                for _do in do_eat:
                    rels_doeat.append([disease, _do])  # 将”疾病-宜吃食品“关系添加到关系列表中

                foods += do_eat  # 更新”食品“实体列表foods

                recommand_eat = data_json['recommand_eat']
                for _recommand in recommand_eat:
                    rels_recommandeat.append([disease, _recommand])  # 将”疾病-推荐食品“关系添加到关系列表中
                foods += recommand_eat  # 更新”食品“实体列表foods

            if 'check' in data_json:
                check = data_json['check']
                for _check in check:
                    rels_check.append([disease, _check])  # 将”疾病-检查项目“关系添加到关系列表中
                checks += check  # 更新“检查项目”关系列表

            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail]
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                producers += producer  # 将该药品大类添加到实体列表中
            disease_infos.append(disease_dict)
        # 返回根据数据库更新信息完毕的实体列表，关系列表，记录各疾病属性的列表disease_infos
        return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), disease_infos,\
               rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,\
               rels_symptom, rels_acompany, rels_category

    '''建立节点'''
    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return

    '''创建知识图谱中心疾病的节点'''
    def create_diseases_nodes(self, disease_infos):
        count = 0
        for disease_dict in disease_infos:
            node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'],
                        prevent=disease_dict['prevent'] ,cause=disease_dict['cause'],
                        easy_get=disease_dict['easy_get'],cure_lasttime=disease_dict['cure_lasttime'],
                        cure_department=disease_dict['cure_department']
                        ,cure_way=disease_dict['cure_way'] , cured_prob=disease_dict['cured_prob'])
            self.g.create(node)
            count += 1
            print(count)
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        # 读取json文件获得表示各实体，关系，属性的列表
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos,rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_diseases_nodes(disease_infos)  # 创建“disease”实体对应的node
        self.create_node('Drug', Drugs)
        print(len(Drugs))
        self.create_node('Food', Foods)
        print(len(Foods))
        self.create_node('Check', Checks)
        print(len(Checks))
        self.create_node('Department', Departments)
        print(len(Departments))
        self.create_node('Producer', Producers)
        print(len(Producers))
        self.create_node('Symptom', Symptoms)
        return

    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''创建实体关系边'''
    def create_graphrels(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
        self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
        self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
        self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')



    '''导出数据'''
    def export_data(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        f_drug = open('drug.txt', 'w+')
        f_food = open('food.txt', 'w+')
        f_check = open('check.txt', 'w+')
        f_department = open('department.txt', 'w+')
        f_producer = open('producer.txt', 'w+')
        f_symptom = open('symptoms.txt', 'w+')
        f_disease = open('disease.txt', 'w+')

        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_department.write('\n'.join(list(Departments)))
        f_producer.write('\n'.join(list(Producers)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_food.close()
        f_check.close()
        f_department.close()
        f_producer.close()
        f_symptom.close()
        f_disease.close()

        return


if __name__ == '__main__':
    handler = MedicalGraph()
    print("step1:导入图谱节点中")
    handler.create_graphnodes()
    print("step2:导入图谱边中")      
    handler.create_graphrels()
    
