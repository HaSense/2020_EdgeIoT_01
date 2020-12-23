from elasticsearch import Elasticsearch
import time
import datetime
import json

class ES:

    #elasticsearch make index
    def __init__(self):
        #elasticsearch running pc ip address and default port 9200
        self.es = Elasticsearch("http://192.168.100.10:9200/") 
        self.index_name = 'mask_wear'
        #self.es.info()


    def make_index(self):

        with open('mapping.json', 'r') as f:
            mapping = json.load(f)            
        
        self.es.indices.create(index = self.index_name,  body = mapping)
    
    def insert_data(self, doc):

        date_time = datetime.datetime.now()
        date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
        doc['date'] = str(date_time)

        '''
        doc1 = {'date': date_time,
                'image_save': 'test',
                'mask_duplication': 7,
                'mask_status': 'test7',
                'nomask_prediction' : 10,
                'nomask_ratio' : 1.1,
                'nosemask_prediction' : 11,
                'nosemask_ratio' : 2.2,
                'visitent_predintion' : 22
                }
        '''
        self.es.index(index = self.index_name, body = doc)
        self.es.indices.refresh(index=self.index_name)

    def search_all(self):

        index = self.index_name
        body =  {
                "sort": [
                    { "date" : 
                     {
                        "order" : "asc"
                     }
                    }
                ],
                "query":{"match_all":{}}
            }
        res = self.es.search(index = index, body = body)
        #print(res['hits']['hits'])
        for result in res['hits']['hits']:
            print(json.dumps(result['_source'], indent=1))

    def search_matched_data(self, key, value):

        result_list = []
        
        index = self.index_name
        body =  {
            "query": {
                "match": {
                key : value
                }
            }
        }

        res_filter = self.es.search(index = index, body = body)

        for result in res_filter['hits']['hits']:
            tmp_data = json.dumps(result['_source'], indent=1)
            print(tmp_data)
            result_list.append(tmp_data)
        return result_list

    def delete_index(self):

        self.es = Elasticsearch("http://192.168.100.10:9200/")
        self.es.indices.delete(index=self.index_name)

    def server_health_check(self):
        cls_check = self.es.cluster.health()
        print(json.dumps(cls_check, indent=1))
        
    def datetime_search_fromES(self):
        
        index = self.index_name
        now = datetime.datetime.now()
        lt = now.strftime('%Y-%m-%d %H:%M:%S')
        
        gte = now.replace(minute=0, hour=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
        
        result_list = []
        
        query = {
            "sort": [
                { "date" : 
                 {
                    "order" : "asc"
                 }
                }
            ],
            "query":{
                "range":{
                    "date":{
                        "gte":str(gte), 
                        "lt":str(lt) # 저장된 데이터 형태
                        #"time_zone": "+09:00" # UTC가 기본이며 -> korea timezone 설정
                    }
                },
            },
        }
        res_filter = self.es.search(index = index, body = query)
        for result in res_filter['hits']['hits']:
            tmp_data = json.dumps(result['_source'], indent=1)
            #print(tmp_data)
            result_list.append(tmp_data)
        return result_list