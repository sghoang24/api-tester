"""Main."""

import argparse
from http_client import HTTPClient
from constants import DAI_COOKIES, SIT_COOKIES, UAT_COOKIES
from utils import get_base_url


def parse_args():
    """Parse arguments."""
    parser = argparse.ArgumentParser(description="Run HTTP client for different environments.")
    parser.add_argument("--env", "-e", choices=["DAI", "SIT", "UAT"], default="DAI", help="Environment to run (default: DAI)")
    return parser.parse_args()


def get_client(env, module: str = "EX"):
    """Get client."""
    if env == "DAI":
        cookies = DAI_COOKIES
    elif env == "SIT":
        cookies = SIT_COOKIES
    else:
        cookies = UAT_COOKIES
    base_url = get_base_url(env)
    if module == "EX":
        base_url += "/assessment/api/v1"
    elif module == "AD":
        base_url += "/administration/api/v1"
    return HTTPClient(base_url, cookies=cookies)


def get_subject_components(client):
    """Get subject components."""
    try:
        payload = {
            "semesterId": "01976233-54b1-7b09-a782-dd589f0624eb",
            "subjectId": "d53ec2f2-1420-47db-a7ee-bb671be75bb5",
            "query": "",
        }
        response = client.request(
            method="POST",
            endpoint="/subjectcomponent/list",
            json_data=payload
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def get_student_group_info(client):
    """Get student group info."""
    try:
        payload = {
            "semesterId": "01976233-54b1-7b09-a782-dd589f0624eb",
            "subjectId": "65975fb9-6be5-42b8-9f89-c36057a55952",
            "studentIds": [
                "e87c7cfb-c081-45d3-b0e9-24e4cc51a975",
                "2426cfc9-5bed-4c29-b9a4-dc96cfe0ff91",
                "a28706b6-d44c-4883-a6c7-b8debdfd6b20",
                "3e05111d-5d82-46be-abef-8d130051eee3",
                "ba328178-4e1f-4e2c-8ee0-2d1256e91896",
                "c52ce8d1-ff6e-4cd1-9f9e-eba6082017cd",
                "de1551a1-91ef-4e74-9b27-b1d89ae4c34f",
                "01e8a32f-6c8b-444e-95e7-5bf463901da3",
                "c74df6c3-f489-4475-8113-35c78197e5b1",
                "a1b5a956-6a7f-4701-adbf-10949960a0ab",
            ]
        }
        response = client.request(
            method="POST",
            endpoint="/studentsubjectmark/studentgroupinfo",
            json_data=payload
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def fake_student_flow(client):
    """Fake student flow."""
    try:
        payload = {
            "semesterId": "01971a27-e9f3-77a0-bf54-484f9a4bd1d8",
            "courseCode": "2605 snow ",
            "subjectIds": [
                "968cab22-3dd1-469e-8456-34496b07820a", # DEV7
                "235e667a-fab9-4da6-93cb-824f3bea9489", # DEV70529
                "0c55727a-ab4d-44e8-8e53-86da9a4c520f", # DEV7DAILY
            ]
        }
        response = client.request(
            method="POST",
            endpoint="/assessmentstudentinfo/devcreate",
            json_data=payload
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def generate_mark(client):
    """Generate mark."""
    try:
        payload = {
            "semesterId": "01971a27-e9f3-77a0-bf54-484f9a4bd1d8",
            "subjectId": "968cab22-3dd1-469e-8456-34496b07820a",
            # "subjectId": "235e667a-fab9-4da6-93cb-824f3bea9489",
            # "subjectId": "0c55727a-ab4d-44e8-8e53-86da9a4c520f",
            "minMarkPercentage": 60,
        }
        response = client.request(
            method="GET",
            endpoint="/assessmentmarkentry/devcreatedata",
            params=payload,
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def sync_weightage(client):
    """Sync weightage."""
    try:
        response = client.request(
            method="GET",
            endpoint="/subjectcomponent/syncweightage",
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def clean_student_distinction(client):
    """Clean student distinction."""
    try:
        payload = {
            "semesterId": "01974399-0551-7971-8b9d-ff703fcc49a0",
            "subjectIds": [
                # "0197b047-4130-7577-b993-ed00524d9118",
                "0197b035-fb12-75cf-8aba-b00a6d06d231",
                "0197b035-2759-7b9a-bd3d-1ae649981719",
                "0197b032-7fb7-7061-b4a4-0f2e8791ee1a",
                "0197b006-155c-77fe-b5f2-487febe20e21",
                "0197b037-0b21-7ce9-8dba-b4e8633983b3",
                "0197b03a-2256-7664-bd33-9e4ef069bacd",
            ]
        }
        response = client.request(
            method="POST",
            endpoint="/subjectawarddistinction/devcleandatastudentdistinction",
            json_data=payload,
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def get_student_group_info(client):
    """Get student group info."""
    try:
        payload = {
            "semesterId": "01975893-768e-7ff4-9a7b-fc5e1dbcfe9a",
            "subjectId": "019787c8-cf75-7987-8364-eca49692ade2",
            "studentIds": [
                "4a753729-da19-4c96-bfb3-012aea659981"
            ]
        }
        response = client.request(
            method="POST",
            endpoint="/studentsubjectmark/studentgroupinfo",
            json_data=payload,
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def incomplete_reminding(client):
    """Incomplete ME reminding."""
    try:
        # DAI
        # payload = {
        #     "semesterId": "01971a27-e9f3-77a0-bf54-484f9a4bd1d8",
        #     "subjectId": "0c55727a-ab4d-44e8-8e53-86da9a4c520f",
        #     "currentDate": "2025-07-17T02:30:00.000Z"
        # }
        
        # SIT
        payload = {
            "semesterId": "0197ab9b-05c5-7ccb-9888-5876b6c1a34e",
            "subjectId": "01983507-72f8-7cd6-a4c1-199f2b891506",
            "currentDate": "2025-07-23T05:00:00.000Z"
        }
        response = client.request(
            method="POST",
            endpoint="/studentcomponentmark/devincompletereminding",
            json_data=payload,
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def course_award_dwm(client):
    """Create course award DWM."""
    try:
        # DAI
        payload = {
            "semesterId": "01971a27-e9f3-77a0-bf54-484f9a4bd1d8",
        }
        response = client.request(
            method="GET",
            endpoint="/courseawarddiplomamerit/devcreate",
            params=payload,
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def random_acad_standing(client):
    """Create course award DWM."""
    try:
        # DAI
        # payload = {
        #     "courses": [
        #         {
        #             "courseId": "01970a9c-ed4b-7912-97b9-68190d16511d",
        #             "semesterId": "01971a27-e9f3-77a0-bf54-484f9a4bd1d8"
        #         }
        #     ],
        #     "numberOfRandom": 12,
        #     "topX": 20
        # }
        # SIT
        payload = {
            "courses": [
                # {
                #     "courseId": "019807eb-a6eb-742e-84bc-3ccba33ec1c6", # J01
                #     # "courseId": "019786c7-e630-7586-8604-5c241faa0dd9",
                #     "semesterId": "0197ab9b-05c5-7ccb-9888-5876b6c1a34e"
                # },
                # {
                #     # "courseId": "019807eb-a6eb-742e-84bc-3ccba33ec1c6", # J01
                #     # "courseId": "01980807-e777-7c33-b9d4-a76c719f2de0", # MN2
                #     # "courseId": "019786c7-e630-7586-8604-5c241faa0dd9",
                #     "courseId" : "0197e904-3ed3-746c-9966-297d50a0b7fd", # TA2
                #     "semesterId": "0197ab9b-05c5-7ccb-9888-5876b6c1a34e"
                # }
                # {
                #     "courseId": "01983a9e-f90b-724d-a279-8ce450b0bcb3", # SE3
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983ac0-0448-7b0a-a0d2-e9f3b276e03b", # SE5
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983a96-3e2f-7362-b8e1-5081b1284445",   # PA1
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983a96-dea6-7006-9616-299790040d2f",   # PA2
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                {
                    "courseId": "01983a9a-f59e-73ca-9013-82e4b50b161b",   # PA3
                    "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                },
                # {
                #     "courseId": "01983aaa-5849-7a28-99ef-06db3ce3afa1",   # J05
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983aac-813b-75f9-b0ee-f612de87a9ea",   # J06
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983aad-43b8-7c05-82c1-87cffd9b4ef8",   # J07
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "0198313d-85e1-72d2-ab0c-593502e4a8ec",   # JM1
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983ab3-a6c5-75c8-9f7b-4b30981aebbd",   # K22
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983ab4-4e3c-7279-9576-aa7d31a352aa",   # K23
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983ab5-2700-7a23-a080-60147db09afa",   # K24
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983ab5-f743-7c43-ba97-b27dd09fdaf2",   # K25
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
                # {
                #     "courseId": "01983a89-a98f-70f6-b7ab-897790c1113f",   # LD3
                #     "semesterId": "0197e819-2a9f-7971-a123-de5f173bc52e"
                # },
            ],
            "numberOfRandom": 18,
            "topX": 25
        }
        
        response = client.request(
            method="POST",
            endpoint="/processingresult/devrandomacadstanding",
            json_data=payload,
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


def sync_percentage(client):
    """Sync percentage for award distinction."""
    try:
        response = client.request(
            method="GET",
            endpoint="/subjectawarddistinction/syncpercentage",
        )
        client.pretty_print(response)
    except Exception as ex:
        print(f"Request failed: {ex}")


# RUN cmd: python main.py -e DAI/SIT/UAT
if __name__ == "__main__":
    args = parse_args()
    client = get_client(
        args.env,
        # "DAI",
        # "SIT",
        # "UAT"
        module="AD"
    )

    # get_subject_components(client)
    # get_student_group_info(client)
    # fake_student_flow(client)
    # generate_mark(client)
    # sync_weightage(client)
    # clean_student_distinction(client)
    # get_student_group_info(client)
    # sync_percentage(client)
    
    # Reminding incomplete MarkEntry
    # incomplete_reminding(client)
    
    # Award DWM
    # course_award_dwm(client)
    random_acad_standing(client)
