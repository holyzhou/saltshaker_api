# -*- coding:utf-8 -*-
from flask_restful import Resource, reqparse
from flask import g
from common.log import Logger
from common.audit_log import audit_log
from common.utility import salt_api_for_product
from common.sso import access_required
from common.const import role_dict
import os

logger = Logger()

parser = reqparse.RequestParser()
parser.add_argument("product_id", type=str, required=True, trim=True)
parser.add_argument("action", type=str, trim=True)
parser.add_argument("jid", type=str, trim=True)


class Job(Resource):
    @access_required(role_dict["common_user"])
    def get(self, job_id):
        args = parser.parse_args()
        salt_api = salt_api_for_product(args["product_id"])
        if isinstance(salt_api, dict):
            return salt_api, 500
        else:
            result = salt_api.jobs_info(job_id)
            return result, 200


class JobList(Resource):
    @access_required(role_dict["common_user"])
    def get(self):
        args = parser.parse_args()
        salt_api = salt_api_for_product(args["product_id"])
        if isinstance(salt_api, dict):
            return salt_api, 500
        else:
            result = salt_api.jobs_list()
            return result, 200


class JobManager(Resource):
    @access_required(role_dict["common_user"])
    def get(self):
        args = parser.parse_args()
        salt_api = salt_api_for_product(args["product_id"])
        if isinstance(salt_api, dict):
            return salt_api, 500
        else:
            result = salt_api.runner("jobs.active")
            return result, 200

    @access_required(role_dict["common_user"])
    def delete(self):
        args = parser.parse_args()
        salt_api = salt_api_for_product(args["product_id"])
        user = g.user_info["username"]
        if isinstance(salt_api, dict):
            return salt_api, 500
        else:
            if args["action"] == "kill" and args["jid"]:
                kill = "salt '*' saltutil.kill_job" + " " + args["jid"]
                try:
                    result = os.popen(kill).read()
                    audit_log(user, args["jid"], args["product_id"], "job id", "kill")
                    return {"status": True, "message": result}, 200
                except Exception as e:
                    return {"status": False, "message": str(e)}, 500
            else:
                return {"status": False, "message": "The specified job id does not exist or arguments error"}, 400
