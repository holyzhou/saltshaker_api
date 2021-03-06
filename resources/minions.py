# -*- coding:utf-8 -*-
from flask_restful import Resource, reqparse
from flask import g
from common.log import Logger
from common.audit_log import audit_log
from common.utility import salt_api_for_product
from common.sso import access_required
from common.const import role_dict

logger = Logger()

parser = reqparse.RequestParser()
parser.add_argument("product_id", type=str, required=True, trim=True)
parser.add_argument("action", type=str, trim=True)
parser.add_argument("minion_id", type=str, trim=True, action="append")
parser.add_argument("minion", type=str, trim=True)
parser.add_argument("item", type=str, trim=True)


class MinionsStatus(Resource):
    @access_required(role_dict["common_user"])
    def get(self):
        args = parser.parse_args()
        salt_api = salt_api_for_product(args["product_id"])
        if isinstance(salt_api, dict):
            return salt_api, 500
        else:
            result = salt_api.runner_status("status")
            return result, 200


class MinionsKeys(Resource):
    @access_required(role_dict["common_user"])
    def get(self):
        args = parser.parse_args()
        salt_api = salt_api_for_product(args["product_id"])
        if isinstance(salt_api, dict):
            return salt_api, 500
        else:
            result = salt_api.list_all_key()
            return result, 200

    @access_required(role_dict["common_user"])
    def post(self):
        args = parser.parse_args()
        salt_api = salt_api_for_product(args["product_id"])
        user = g.user_info["username"]
        if isinstance(salt_api, dict):
            return salt_api
        else:
            result_list = []
            if args["action"] and args["minion_id"]:
                if args["action"] == "accept":
                    for minion in args["minion_id"]:
                        result = salt_api.accept_key(minion)
                        result_list.append({minion: result})
                        audit_log(user, minion, args["product_id"], "minion", "accept")
                    return {"status": result_list, "message": ""}, 200
                if args["action"] == "reject":
                    for minion in args["minion_id"]:
                        result = salt_api.reject_key(minion)
                        result_list.append({minion: result})
                        audit_log(user, minion, args["product_id"], "minion", "reject")
                    return {"status": result_list, "message": ""}, 200
                if args["action"] == "delete":
                    for minion in args["minion_id"]:
                        result = salt_api.delete_key(minion)
                        result_list.append({minion: result})
                        audit_log(user, minion, args["product_id"], "minion", "delete")
                    return {"status": result_list, "message": ""}, 200
            else:
                return {"status": False,
                        "message": "Missing required parameter in the JSON body or "
                                   "the post body or the query string"}, 400


class MinionsGrains(Resource):
    @access_required(role_dict["common_user"])
    def get(self):
        args = parser.parse_args()
        salt_api = salt_api_for_product(args["product_id"])
        if isinstance(salt_api, dict):
            return salt_api, 500
        else:
            if args["minion"]:
                if args["item"]:
                    result = salt_api.grain(args["minion"], args["item"])
                    if result:
                        return result
                    return {"status": False, "message": "The specified minion does not exist"}, 404
                else:
                    result = salt_api.grains(args["minion"])
                    if result:
                        return result
                    return {"status": False, "message": "The specified minion does not exist"}, 404
            else:
                return {"status": False, "message": "The specified minion arguments error"}, 400

