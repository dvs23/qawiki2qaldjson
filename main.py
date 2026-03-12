import json
from argparse import ArgumentParser

import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON



PREFIXES = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX schema: <http://schema.org/>
PREFIX cc: <http://creativecommons.org/ns#>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wd: <https://qawiki.org/entity/>
PREFIX data: <http://qawiki.org/wiki/Special:EntityData/>
PREFIX s: <https://qawiki.org/entity/statement/>
PREFIX ref: <https://qawiki.org/reference/>
PREFIX v: <https://qawiki.org/value/>
PREFIX wdt: <https://qawiki.org/prop/direct/>
PREFIX wdtn: <https://qawiki.org/prop/direct-normalized/>
PREFIX p: <https://qawiki.org/prop/>
PREFIX ps: <https://qawiki.org/prop/statement/>
PREFIX psv: <https://qawiki.org/prop/statement/value/>
PREFIX psn: <https://qawiki.org/prop/statement/value-normalized/>
PREFIX pq: <https://qawiki.org/prop/qualifier/>
PREFIX pqv: <https://qawiki.org/prop/qualifier/value/>
PREFIX pqn: <https://qawiki.org/prop/qualifier/value-normalized/>
PREFIX pr: <https://qawiki.org/prop/reference/>
PREFIX prv: <https://qawiki.org/prop/reference/value/>
PREFIX prn: <https://qawiki.org/prop/reference/value-normalized/>
PREFIX wdno: <https://qawiki.org/prop/novalue/>
"""

WIKIDATAPREFIXES = """PREFIX bd: <http://www.bigdata.com/rdf#>
PREFIX cc: <http://creativecommons.org/ns#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX mwapi: <https://www.mediawiki.org/ontology#API/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX pqn: <http://www.wikidata.org/prop/qualifier/value-normalized/>
PREFIX pqv: <http://www.wikidata.org/prop/qualifier/value/>
PREFIX pr: <http://www.wikidata.org/prop/reference/>
PREFIX prn: <http://www.wikidata.org/prop/reference/value-normalized/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX prv: <http://www.wikidata.org/prop/reference/value/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX psn: <http://www.wikidata.org/prop/statement/value-normalized/>
PREFIX psv: <http://www.wikidata.org/prop/statement/value/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdata: <http://www.wikidata.org/wiki/Special:EntityData/>
PREFIX wdno: <http://www.wikidata.org/prop/novalue/>
PREFIX wdsubgraph: <https://query.wikidata.org/subgraph/>
PREFIX wdref: <http://www.wikidata.org/reference/>
PREFIX wds: <http://www.wikidata.org/entity/statement/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wdtn: <http://www.wikidata.org/prop/direct-normalized/>
PREFIX wdv: <http://www.wikidata.org/value/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
"""

def get_question_entities(g):
    knows_query = f"""
    {PREFIXES}
    SELECT DISTINCT ?question
    WHERE {{
        ?question wdt:P1 wd:Q1 . 
    }}"""

    qres = g.query(knows_query)
    return [str(row.question) for row in qres]

def get_question_of_entity(g, entity, lang="en"):
    knows_query = f"""
        {PREFIXES}
        SELECT DISTINCT ?question
        WHERE {{
            <{entity}> rdfs:label ?question .
            FILTER(LANG(?question) = "{lang}") 
        }}"""

    qres = g.query(knows_query)
    res = [{"string": row.question.value, "language": row.question.language} for row in qres]
    assert len(res) == 1
    return res[0]

def get_query_of_entity(g, entity):
    knows_query = f"""
        {PREFIXES}
        SELECT DISTINCT ?query
        WHERE {{
            <{entity}> wdt:P11 ?query .
        }}"""

    qres = g.query(knows_query)
    res = [{"sparql": row.query.value} for row in qres]
    assert len(res) == 1
    return res[0]

def get_mentions(g, entity, question=None, lang="en"):
    knows_query = f"""
        {PREFIXES}
        SELECT DISTINCT ?mention ?entityuri ?propertyuri ?invpropertyuri ?maxpropertyuri ?minpropertyuri ?valpropertyuri ?existspropertyuri ?notexistspropertyuri ?notexistsinvpropertyuri ?existsinvpropertyuri ?subpropertyuri ?superpropertyuri ?objproppropertyuri ?objvalpropertyuri
        WHERE {{
            <{entity}> p:P38 ?stmt .
            ?stmt ps:P38 ?mention .
            OPTIONAL {{ ?stmt pq:P17 ?entityuri }} .
            OPTIONAL {{ ?stmt pq:P18 ?propertyuri }} .
            OPTIONAL {{ ?stmt pq:P45 ?invpropertyuri }} .            
            OPTIONAL {{ ?stmt pq:P48 ?maxpropertyuri }} .            
            OPTIONAL {{ ?stmt pq:P49 ?minpropertyuri }} .            
            OPTIONAL {{ ?stmt pq:P50 ?valpropertyuri }} . 
            OPTIONAL {{ ?stmt pq:P51 ?existspropertyuri }} . 
            OPTIONAL {{ ?stmt pq:P52 ?notexistspropertyuri }} . 
            OPTIONAL {{ ?stmt pq:P56 ?notexistsinvpropertyuri }} .
            OPTIONAL {{ ?stmt pq:P55 ?existsinvpropertyuri }} .
            OPTIONAL {{ ?stmt pq:P58 ?subpropertyuri }} .
            OPTIONAL {{ ?stmt pq:P59 ?superpropertyuri }} .
            OPTIONAL {{ ?stmt pq:P62 ?objproppropertyuri . ?stmt pq:P63 ?objvalpropertyuri }} .
            FILTER(LANG(?mention) = "{lang}") 
        }}"""

    qres = g.query(knows_query)
    res = []
    for row in qres:
        if question is None or row.mention.value.lower() in question.lower():
            curr_res = {"string": row.mention.value, "language": row.mention.language}# mention: ps:p38
            if row.entityuri is not None:#pq:P17
                curr_res["entity"] = "http://www.wikidata.org/entity/" + row.entityuri.value
            if row.propertyuri is not None:#pq:P18
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.propertyuri.value
            if row.invpropertyuri is not None:#pq:P45
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.invpropertyuri.value
                curr_res["inverse"] = True
            if row.maxpropertyuri is not None:#pq:P48
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.maxpropertyuri.value
                curr_res["superlative"] = "max"
            if row.minpropertyuri is not None:#pq:P49
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.minpropertyuri.value
                curr_res["superlative"] = "min"
            if row.valpropertyuri is not None:#pq:P50
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.valpropertyuri.value
                curr_res["mention"] = "implicit"
            if row.existspropertyuri is not None:#pq:P51
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.existspropertyuri.value
                curr_res["quantifier"] = "exists"
            if row.notexistspropertyuri is not None:#pq:P52
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.notexistspropertyuri.value
                curr_res["quantifier"] = "not exists"
            if row.notexistsinvpropertyuri is not None:#pq:P56
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.notexistsinvpropertyuri.value
                curr_res["quantifier"] = "not exists"
                curr_res["inverse"] = True
            if row.existsinvpropertyuri is not None:#pq:P55
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.existsinvpropertyuri.value
                curr_res["quantifier"] = "exists"
                curr_res["inverse"] = True
            if row.subpropertyuri is not None:#pq:P58
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.subpropertyuri.value
                curr_res["mention"] = "subproperty"
            if row.superpropertyuri is not None:#pq:P59
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.superpropertyuri.value
                curr_res["mention"] = "superproperty"
            if row.objproppropertyuri is not None and row.objvalpropertyuri is not None:#pq:P62 pq:P63
                curr_res["property"] = "http://www.wikidata.org/prop/" + row.objproppropertyuri.value
                curr_res["mention"] = "implicit"
                curr_res["quantifier"] = "hasvalue"
                curr_res["value"] = row.objvalpropertyuri.value

            if len(curr_res) > 2: # neither propert nor entity would be useless
                res.append(curr_res)

    return res

def get_results(query, endpoint):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(WIKIDATAPREFIXES+query)
    sparql.setReturnFormat(JSON)
    res = sparql.query().convert()
    keys = list(res.keys())
    for k in keys:
        if k in ["meta"]:
            res.pop(k)
    if "results" in res and len(res["results"]["bindings"]) == 0:
        print(f"Error: Empty result for query {query}")
    return res

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--endpoint", type=str, default="http://localhost:8890/sparql")
    argparser.add_argument("--ttlfile", type=str, default="./qawiki-v1-complete-2025-09-09.ttl")
    argparser.add_argument("--outpath", type=str, default="./wikikgqa.json")

    arguments = argparser.parse_args()
    g = rdflib.Graph()
    g.parse(arguments.ttlfile)

    res = []

    for idx, qe in enumerate(get_question_entities(g)):
        qen = get_question_of_entity(g, qe, "en")
        qes = get_question_of_entity(g, qe, "es")
        query = get_query_of_entity(g, qe)
        row = {
            "id": idx,
            "question": [qen, qes],
            "query": query,
            "mentions": get_mentions(g, qe, qen["string"], lang="en") + get_mentions(g, qe, qes["string"], lang="es"),
            "answers": [get_results(query["sparql"], arguments.endpoint)],
        }
        print(row)
        res.append(row)

    json.dump({
        "dataset": {
            "id": "wikikgqa2026"
        },
        "questions": res
    }, open(arguments.outpath, "w"))
