"""
Basic Apache agent smoke test suite
"""
import unittest
from lib.agent_utils import process_autosubmit_form
from requests import get, post, session

from config.ProductConfig import NginxAgentConfig, AMConfig


class NginxAgentSmoke(unittest.TestCase):
    agent_cfg = NginxAgentConfig()
    amcfg = AMConfig()
    policy_url = '/policy.html'
    deny_policy_url = '/deny.html'
    neu_url = '/neu.html'

    def test_redirect(self):
        resp = get(url=self.agent_cfg.agent_url, allow_redirects=False)
        self.assertEqual(302, resp.status_code, 'Expecting 302 redirect to AM login')
        self.assertTrue('openam' in resp.headers.get('location'), 'Expecting openam to be in location header')

    def test_access_allowed_resource(self):
        s = session()
        s.headers = {'X-OpenAM-Username': 'user.1', 'X-OpenAM-Password': 'password',
                     'Content-Type': 'application/json', 'Accept-API-Version': 'resource=2.0, protocol=1.0'}
        resp = s.post(url=self.amcfg.rest_authn_url, headers=s.headers)
        self.assertEqual(200, resp.status_code, 'User needs to login')

        resp = s.get(self.agent_cfg.agent_url + self.policy_url)
        self.assertEqual(200, resp.status_code, 'Expecting HTTP-200 from autosubmit page')

        r = process_autosubmit_form(resp, s)
        self.assertTrue('Policy testing page' in r.text, "Expecting Policy testing page string")
        self.assertEqual(200, r.status_code, "Expecting HTTP-200 in response")

        s.close()

    def test_access_denied_resource(self):
        s = session()
        s.headers = {'X-OpenAM-Username': 'user.1', 'X-OpenAM-Password': 'password',
                   'Content-Type': 'application/json', 'Accept-API-Version': 'resource=2.0, protocol=1.0'}
        resp = s.post(url=self.amcfg.rest_authn_url, headers=s.headers)
        self.assertEqual(200, resp.status_code, 'User login, expecting HTTP-200')

        resp = s.get(self.agent_cfg.agent_url + self.deny_policy_url)
        r = process_autosubmit_form(resp, s)
        self.assertEqual(403, r.status_code, 'Expecting HTTP-403 when accessing allowed resource')

        s.close()

    def test_access_neu_url(self):
        resp = get(self.agent_cfg.agent_url + self.neu_url)
        self.assertEqual(200, resp.status_code, "Expecting to have access to NEU url")
