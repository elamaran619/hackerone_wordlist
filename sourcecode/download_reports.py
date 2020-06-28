#!/usr/bin/env python
# coding: utf-8
# github.com/xyele

from banner import *

import argparse,json,requests,base64,pyfiglet

parser = argparse.ArgumentParser()
parser.add_argument('--idrange', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()

try:
    id_range = str(args.idrange).split(",") # 25,10000
    id_start = int(id_range[0]) # 25
    id_end = int(id_range[1]) # 10000

    req_headers = {"content-type":"application/json","X-Auth-Token":"----","Content-Length":"0"}
    req_template = "{\"operationName\":\"HacktivityPageQuery\",\"variables\":{\"querystring\":\"\",\"where\":{\"report\":{\"disclosed_at\":{\"_is_null\":false}}},\"orderBy\":null,\"secureOrderBy\":{\"latest_disclosable_activity_at\":{\"_direction\":\"ASC\"}},\"count\":25,\"maxShownVoters\":10,\"cursor\":\"[B64ENCODEDID]\"},\"query\":\"query HacktivityPageQuery($querystring: String, $orderBy: HacktivityItemOrderInput, $secureOrderBy: FiltersHacktivityItemFilterOrder, $where: FiltersHacktivityItemFilterInput, $count: Int, $cursor: String, $maxShownVoters: Int) {\\n  me {\\n    id\\n    __typename\\n  }\\n  hacktivity_items(first: $count, after: $cursor, query: $querystring, order_by: $orderBy, secure_order_by: $secureOrderBy, where: $where) {\\n    total_count\\n    ...HacktivityList\\n    __typename\\n  }\\n}\\n\\nfragment HacktivityList on HacktivityItemConnection {\\n  total_count\\n  pageInfo {\\n    endCursor\\n    hasNextPage\\n    __typename\\n  }\\n  edges {\\n    node {\\n      ... on HacktivityItemInterface {\\n        id\\n        databaseId: _id\\n        ...HacktivityItem\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment HacktivityItem on HacktivityItemUnion {\\n  type: __typename\\n  ... on HacktivityItemInterface {\\n    id\\n    votes {\\n      total_count\\n      __typename\\n    }\\n    voters: votes(last: $maxShownVoters) {\\n      edges {\\n        node {\\n          id\\n          user {\\n            id\\n            username\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    upvoted: upvoted_by_current_user\\n    __typename\\n  }\\n  ... on Undisclosed {\\n    id\\n    ...HacktivityItemUndisclosed\\n    __typename\\n  }\\n  ... on Disclosed {\\n    id\\n    ...HacktivityItemDisclosed\\n    __typename\\n  }\\n  ... on HackerPublished {\\n    id\\n    ...HacktivityItemHackerPublished\\n    __typename\\n  }\\n}\\n\\nfragment HacktivityItemUndisclosed on Undisclosed {\\n  id\\n  reporter {\\n    id\\n    username\\n    ...UserLinkWithMiniProfile\\n    __typename\\n  }\\n  team {\\n    handle\\n    name\\n    medium_profile_picture: profile_picture(size: medium)\\n    url\\n    id\\n    ...TeamLinkWithMiniProfile\\n    __typename\\n  }\\n  latest_disclosable_action\\n  latest_disclosable_activity_at\\n  requires_view_privilege\\n  total_awarded_amount\\n  currency\\n  __typename\\n}\\n\\nfragment TeamLinkWithMiniProfile on Team {\\n  id\\n  handle\\n  name\\n  __typename\\n}\\n\\nfragment UserLinkWithMiniProfile on User {\\n  id\\n  username\\n  __typename\\n}\\n\\nfragment HacktivityItemDisclosed on Disclosed {\\n  id\\n  reporter {\\n    id\\n    username\\n    ...UserLinkWithMiniProfile\\n    __typename\\n  }\\n  team {\\n    handle\\n    name\\n    medium_profile_picture: profile_picture(size: medium)\\n    url\\n    id\\n    ...TeamLinkWithMiniProfile\\n    __typename\\n  }\\n  report {\\n    id\\n    title\\n    substate\\n    url\\n    __typename\\n  }\\n  latest_disclosable_action\\n  latest_disclosable_activity_at\\n  total_awarded_amount\\n  severity_rating\\n  currency\\n  __typename\\n}\\n\\nfragment HacktivityItemHackerPublished on HackerPublished {\\n  id\\n  reporter {\\n    id\\n    username\\n    ...UserLinkWithMiniProfile\\n    __typename\\n  }\\n  team {\\n    id\\n    handle\\n    name\\n    medium_profile_picture: profile_picture(size: medium)\\n    url\\n    ...TeamLinkWithMiniProfile\\n    __typename\\n  }\\n  report {\\n    id\\n    url\\n    title\\n    substate\\n    __typename\\n  }\\n  latest_disclosable_activity_at\\n  severity_rating\\n  __typename\\n}\\n\"}"
    log("Started to download reports.")

    for i in range(id_start,id_end,25):
        try:
            log(f"[*] Looking for {str(i)}")
            b64encoded_id = base64.b64encode(str(i).encode()).decode("utf-8")
            request_data = req_template.replace("[B64ENCODEDID]",str(b64encoded_id))
            req_headers.update({"Content-Length":str(len(request_data))})
            request = requests.post("https://hackerone.com/graphql",data = request_data,headers=req_headers)
            edges = json.loads(request.text)["data"]["hacktivity_items"]["edges"]
            for e in edges:
                if e["node"]["__typename"] == "Disclosed":
                    report_id = str(e["node"]["databaseId"])
                    report = requests.get("https://hackerone.com/reports/{}.json".format(report_id)).text
                    f = open(f"{str(args.output)}{report_id}.json","w+")
                    f.write(report)
                    f.close()
                    successful(f"[+] Got {report_id}.json")
        except Exception as e_second:
            unsuccessful(f"Got exception: \"{str(e_second)}\"")

except Exception as e_first:
    unsuccessful(f"Got exception: \"{str(e_first)}\"")