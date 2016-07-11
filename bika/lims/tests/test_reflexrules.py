from Products.CMFPlone.utils import _createObjectByType
from plone.app.testing import login, logout
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from bika.lims.testing import BIKA_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase
from bika.lims.utils import tmpID
from bika.lims.workflow import doActionFor
from bika.lims.idserver import renameAfterCreation
import unittest
try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


# Tests related with reflex testing
class TestReflexRules(BikaFunctionalTestCase):
    layer = BIKA_FUNCTIONAL_TESTING
    # A list with the created rules
    rules_list = []
    # A list with the created methods
    methods_list = []
    # A list with the created analysis services
    ans_list = []

    def create_departments(self, department_data):
        """
        Creates a set of departments to be used in the tests
        :department_data: [{
                'title':'xxx',
                },
            ...]
        """
        departments_list = []
        folder = self.portal.bika_setup.bika_departments
        for department_d in department_data:
            _id = folder.invokeFactory('Department', id=tmpID())
            dep = folder[_id]
            dep.edit(
                title=department_d['title'],
                )
            dep.unmarkCreationFlag()
            renameAfterCreation(dep)
            departments_list.append(dep)
        return departments_list

    def create_category(self, category_data):
        """
        Creates a set of analaysis categories to be used in the tests
        :category_data: [{
                'title':'xxx',
                'Department': department object
                },
            ...]
        """
        folder = self.portal.bika_setup.bika_analysiscategories
        categories_list = []
        for category_d in category_data:
            _id = folder.invokeFactory('AnalysisCategory', id=tmpID())
            cat = folder[_id]
            cat.edit(
                title=category_d['title'],
                Department=category_d.get('Department', []),
                )
            cat.unmarkCreationFlag()
            renameAfterCreation(cat)
            categories_list.append(cat)
        return categories_list

    def create_analysisservices(self, as_data):
        """
        Creates a set of analaysis services to be used in the tests
        :as_data: [{
                'title':'xxx',
                'ShortTitle':'xxx',
                'Keyword': 'xxx',
                'PointOfCapture': 'Lab',
                'Category':category object,
                'Methods': [methods object,],
                },
            ...]
        """
        folder = self.portal.bika_setup.bika_analysisservices
        ans_list = []
        for as_d in as_data:
            _id = folder.invokeFactory('AnalysisService', id=tmpID())
            ans = folder[_id]
            ans.edit(
                title=as_d['title'],
                ShortTitle=as_d.get('ShortTitle', ''),
                Keyword=as_d.get('Keyword', ''),
                PointOfCapture=as_d.get('PointOfCapture', 'Lab'),
                Category=as_d.get('Category', ''),
                Methods=as_d.get('Methods', []),
                )
            ans.unmarkCreationFlag()
            renameAfterCreation(ans)
            ans_list.append(ans)
        return ans_list

    def create_methods(self, methods_data):
        """
        Creates a set of methods to be used in the tests
        :methods_data: [{
                'title':'xxx',
                'description':'xxx',
                'Instructions':'xxx',
                'MethodID':'xxx',
                'Accredited':'False/True'},
            ...]
        """
        folder = self.portal.bika_setup.methods
        methods_list = []
        for meth_d in methods_data:
            _id = folder.invokeFactory('Method', id=tmpID())
            meth = folder[_id]
            meth.edit(
                title=meth_d['title'],
                description=meth_d.get('description', ''),
                Instructions=meth_d.get('Instructions', ''),
                MethodID=meth_d.get('MethodID', ''),
                Accredited=meth_d.get('Accredited', True),
                )
            meth.unmarkCreationFlag()
            renameAfterCreation(meth)
            methods_list.append(meth)
        return methods_list

    def create_reflex_rules(self, rules_data):
        """
        Given a dict with raflex rules data, it creates the rules
        :rules_data: [{'title':'xxx','description':'xxx',
            'method':method-obj,
            'ReflexRules': [{'actions': [
                              {'act_row_idx': '1',
                               'action': 'repeat',
                               'analyst': 'analyst1',
                               'otherWS': True},
                              {'act_row_idx': '2',
                               'action': 'duplicate',
                               'analyst': 'analyst1',
                               'otherWS': False}],
                  'analysisservice': 'a9df45163f294b2288a369f43c6b0f95',
                  'discreteresult': '',
                  'range0': '5',
                  'range1': '10',
                  'trigger': 'submit',
                  'value': '8'}],...]}
        """
        # Creating a rule
        rules_list = []
        folder = self.portal.bika_setup.bika_reflexrulefolder
        for rule_d in rules_data:
            _id = folder.invokeFactory('ReflexRule', id=tmpID())
            rule = folder[_id]
            if not rule_d.get('method', ''):
                # Rise an error
                self.fail(
                    'There is need a method in order to create'
                    ' a reflex rule')
            method = rule_d.get('method')
            reflexrules = rule_d.get('ReflexRules', [])
            rule.edit(
                title=rule_d.get('title', ''),
                description=rule_d.get('description', ''),
                )
            rule.setMethod(method.UID())
            if reflexrules:
                rule.setReflexRules(reflexrules)
            rule.unmarkCreationFlag()
            renameAfterCreation(rule)
            rules_list.append(rule)
        return rules_list

    def setUp(self):
        super(TestReflexRules, self).setUp()
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        logout()
        super(TestReflexRules, self).tearDown()

    def test_reflex_rule_set_get(self):
        """
        Testing the analysis service bind and the simple set/get
        data from the widget
        """
        # Creating a department
        department_data = [
            {
                'title': 'dep1',
            }
        ]
        deps = self.create_departments(department_data)
        # Creating a category
        category_data = [{
            'title': 'cat1',
            'Department': deps[0]
            },
        ]
        cats = self.create_category(category_data)
        # Creating a method
        methods_data = [
            {
                'title': 'Method 1',
                'description': 'A description',
                'Instructions': 'An instruction',
                'MethodID': 'm1',
                'Accredited': 'True'
            },
        ]
        meths = self.create_methods(methods_data)
        # Creating an analysis service
        as_data = [{
                'title': 'analysis service1',
                'ShortTitle': 'as1',
                'Keyword': 'as1',
                'PointOfCapture': 'Lab',
                'Category': cats[0],
                'Methods': meths,
                },
        ]
        ans_list = self.create_analysisservices(as_data)
        # Creating a rule
        rules = [{
            'range1': '10', 'range0': '5',
            'discreteresult': '',
            'trigger': 'submit',
            'analysisservice': ans_list[0].UID(), 'value': '8',
                'actions':[{'action':'repeat', 'act_row_idx':'1',
                            'otherWS':True, 'analyst': 'analyst1'},
                          {'action':'duplicate', 'act_row_idx':'2',
                            'otherWS':False, 'analyst': 'analyst1'},
                    ]
        },]
        rules_data = [
            {
                'title': 'Rule MS',
                'description': 'A description',
                'method': meths[0],
                'ReflexRules': rules
            },
        ]
        rules_list = self.create_reflex_rules(rules_data)
        rule = rules_list[-1]
        self.assertTrue(
            ans_list[-1].UID() == rule.getReflexRules()[0].get(
                'analysisservice', '')
            )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestReflexRules))
    suite.layer = BIKA_FUNCTIONAL_TESTING
    return suite
