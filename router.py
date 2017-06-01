# _*_ coding: utf-8_*_
#
# genral application route config:
# simplify the router config by dinamic load class
# by lwz7512
# @2016/05/17

import tornado.web

from foo import comm
from foo.auth import auth_email
from foo.auth import auth_phone
from vendor import vendor_category
from vendor import vendor_activity
from vendor import vendor_order
from vendor import vendor_customer
from vendor import vendor_voucher
from vendor import vendor_setup
from vendor import trip_router
from api import api_category
from api import api_activity
from api import api_setup
from api import api_customer_profile
from api import api_order


def map():

    config = [

        # authenticated
        (r'/ops/auth/email/login', getattr(auth_email, 'AuthEmailLoginHandler')),
        (r'/ops/auth/email/register', getattr(auth_email, 'AuthEmailRegisterHandler')),
        (r'/ops/auth/email/forgot-pwd', getattr(auth_email, 'AuthEmailForgotPwdHandler')),
        (r'/ops/auth/email/reset-pwd', getattr(auth_email, 'AuthEmailResetPwdHandler')),
        (r'/ops/auth/welcome', getattr(auth_email, 'AuthWelcomeHandler')),
        (r'/ops/auth/logout', getattr(auth_email, 'AuthLogoutHandler')),
        (r'/ops/auth/phone/login', getattr(auth_phone, 'AuthPhoneLoginHandler')),
        (r'/ops/auth/phone/register', getattr(auth_phone, 'AuthPhoneRegisterHandler')),
        (r'/ops/auth/phone/verify-code', getattr(auth_phone, 'AuthPhoneVerifyCodeHandler')),
        (r'/ops/auth/phone/lost-pwd', getattr(auth_phone, 'AuthPhoneLostPwdHandler')),


        # vendor category
        (r'/', getattr(vendor_category, 'VendorIndexHandler')),
        (r'/vendors/([a-z0-9]*)/categorys', getattr(vendor_category, 'VendorCategoryListHandler')),
        (r'/vendors/([a-z0-9]*)/categorys/create', getattr(vendor_category, 'VendorCategoryCreateHandler')),
        (r'/vendors/([a-z0-9]*)/categorys/([a-z0-9]*)/edit', getattr(vendor_category, 'VendorCategoryEditHandler')),
        (r'/vendors/([a-z0-9]*)/categorys/([a-z0-9]*)/delete', getattr(vendor_category, 'VendorCategoryDeleteHandler')),

        # vendor activity
        (r'/vendors/([a-z0-9]*)/activitys/draft', getattr(vendor_activity, 'VendorActivityDraftHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/pop', getattr(vendor_activity, 'VendorActivityPopHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/doing', getattr(vendor_activity, 'VendorActivityDoingHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/canceled', getattr(vendor_activity, 'VendorActivityCanceledHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/completed', getattr(vendor_activity, 'VendorActivityCompletedHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/recruit', getattr(vendor_activity, 'VendorActivityRecruitHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/create/step1', getattr(vendor_activity, 'VendorActivityCreateStep1Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/create/step2', getattr(vendor_activity, 'VendorActivityCreateStep2Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/create/step3', getattr(vendor_activity, 'VendorActivityCreateStep3Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step1', getattr(vendor_activity, 'VendorActivityDetailStep1Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step2', getattr(vendor_activity, 'VendorActivityDetailStep2Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step3', getattr(vendor_activity, 'VendorActivityDetailStep3Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step4', getattr(vendor_activity, 'VendorActivityDetailStep4Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step5', getattr(vendor_activity, 'VendorActivityDetailStep5Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step6', getattr(vendor_activity, 'VendorActivityDetailStep6Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step7', getattr(vendor_activity, 'VendorActivityDetailStep7Handler')),

        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step8', getattr(vendor_activity, 'VendorActivityDetailStep8Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/detail/step9', getattr(vendor_activity, 'VendorActivityDetailStep9Handler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/publish', getattr(vendor_activity, 'VendorActivityActionPublishHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/delete', getattr(vendor_activity, 'VendorActivityActionDeleteHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/cancel', getattr(vendor_activity, 'VendorActivityActionCancelHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/reset', getattr(vendor_activity, 'VendorActivityActionResetHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/kickoff', getattr(vendor_activity, 'VendorActivityActionKickoffHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/popular', getattr(vendor_activity, 'VendorActivityActionPopularHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/unpopular', getattr(vendor_activity, 'VendorActivityActionUnpopularHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/complete', getattr(vendor_activity, 'VendorActivityActionCompleteHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/clone', getattr(vendor_activity, 'VendorActivityActionCloneHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/action/evaluate', getattr(vendor_activity, 'VendorActivityActionEvalHandler')),

        # 联盟活动分享
        (r'/vendors/([a-z0-9]*)/activitys/recruit-nothidden', getattr(vendor_activity, 'VendorActivityRecruitNotHiddenHandler')),
        (r'/vendors/([a-z0-9]*)/activity/([a-z0-9]*)/open/set', getattr(vendor_activity, 'VendorActivityOpenSetHandler')),
        (r'/vendors/([a-z0-9]*)/activity/([a-z0-9]*)/open/cancel', getattr(vendor_activity, 'VendorActivityOpenCancelHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/league/share', getattr(vendor_activity, 'VendorActivityLeagueShareHandler')),
        (r'/vendors/([a-z0-9]*)/activity/([a-z0-9]*)/share/set', getattr(vendor_activity, 'VendorActivityShareSetHandler')),
        (r'/vendors/([a-z0-9]*)/activity/([a-z0-9]*)/share/cancel', getattr(vendor_activity, 'VendorActivityShareCancelHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/league/recruit', getattr(vendor_activity, 'VendorActivityLeagueRecruitHandler')),
        (r'/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/demo', getattr(vendor_activity, 'VendorActivityLeagueDemoHandler')),


        # 我自己的全部订单，含分销
        (r"/vendors/([a-z0-9]*)/orders-me-all", getattr(vendor_order, 'VendorOrdersMeAllHandler')),
        # 我自己的订单，不含分销
        (r"/vendors/([a-z0-9]*)/orders-me-none", getattr(vendor_order, 'VendorOrdersMeNoneHandler')),
        # 某人分销我的订单
        (r"/vendors/([a-z0-9]*)/orders-me-other", getattr(vendor_order, 'VendorOrdersMeOtherHandler')),
        # 他人分销我的全部订单
        (r"/vendors/([a-z0-9]*)/orders-me-others", getattr(vendor_order, 'VendorOrdersMeOthersHandler')),
        # 我分销他人的全部订单
        (r"/vendors/([a-z0-9]*)/orders-others-me", getattr(vendor_order, 'VendorOrdersOthersMeHandler')),
        # 我分销某人的订单
        (r"/vendors/([a-z0-9]*)/orders-other-me", getattr(vendor_order, 'VendorOrdersOtherMeHandler')),

        # order
        (r"/vendors/([a-z0-9]*)/orders/([a-z0-9]*)", getattr(vendor_order, 'VendorOrderInfoHandler')),
        (r"/vendors/([a-z0-9]*)/applys", getattr(vendor_order, 'VendorApplyListHandler')),
        (r"/vendors/([a-z0-9]*)/order/vouchers", getattr(vendor_order, 'VendorVoucherOrderListHandler')),

        # 结算
        (r"/vendors/([a-z0-9]*)/supplier-balance", getattr(vendor_order, 'VendorSupplierBalanceHandler')),
        (r"/vendors/([a-z0-9]*)/reseller-balance", getattr(vendor_order, 'VendorResellerBalanceHandler')),

        (r"/vendors/([a-z0-9]*)/league-balance", getattr(vendor_order, 'VendorLeagueBalanceHandler')),
        (r"/vendors/([a-z0-9]*)/apply-cashout-log", getattr(vendor_order, 'VendorApplyCashoutLogHandler')),

        (r"/vendors/([a-z0-9]*)/supplier-details/([a-z0-9]*)", getattr(vendor_order, 'VendorSupplierBalanceDetailsHandler')),
        (r"/vendors/([a-z0-9]*)/reseller-details/([a-z0-9]*)", getattr(vendor_order, 'VendorResellerBalanceDetailsHandler')),
        # 供应商发起提现申请
        (r'/vendors/([a-z0-9]*)/leagues/([a-z0-9]*)/apply-cash-out', getattr(vendor_order, 'VendorSupplierApplyCashoutHandler')),
        # 分销商发起提现申请
        (r'/vendors/([a-z0-9]*)/suppliers/([a-z0-9]*)/apply-cash-out', getattr(vendor_order, 'VendorResellerApplyCashoutHandler')),


        # customer profile
        (r"/vendors/([a-z0-9]*)/customers", getattr(vendor_customer, 'VendorCustomerListHandler')),
        (r"/vendors/([a-z0-9]*)/customers/([a-z0-9]*)", getattr(vendor_customer, 'VendorCustomerProfileHandler')),
        (r"/vendors/([a-z0-9]*)/crets/([a-z0-9]*)", getattr(vendor_customer, 'VendorCustomerCretInfoHandler')),
        (r"/vendors/([a-z0-9]*)/customer/search", getattr(vendor_customer, 'VendorCustomerSearchHandler')),

        # vouchers
        (r"/vendors/([a-z0-9]*)/vouchers", getattr(vendor_voucher, 'VendorVoucherListHandler')),
        (r"/vendors/([a-z0-9]*)/vouchers-free/create", getattr(vendor_voucher, 'VendorVoucherFreeCreateHandler')),
        (r"/vendors/([a-z0-9]*)/vouchers-pay/create", getattr(vendor_voucher, 'VendorVoucherPayCreateHandler')),
        (r"/vendors/([a-z0-9]*)/vouchers-free/([a-z0-9]*)/allocate", getattr(vendor_voucher, 'VendorVoucherFreeAllocateHandler')),
        (r"/vendors/([a-z0-9]*)/vouchers-free/([a-z0-9]*)/edit", getattr(vendor_voucher, 'VendorVoucherFreeEditHandler')),
        (r"/vendors/([a-z0-9]*)/vouchers-pay/([a-z0-9]*)/allocate", getattr(vendor_voucher, 'VendorVoucherPayAllocateHandler')),
        (r"/vendors/([a-z0-9]*)/vouchers-pay/([a-z0-9]*)/edit", getattr(vendor_voucher, 'VendorVoucherPayEditHandler')),

        # setup
        (r"/vendors/([a-z0-9]*)/setup/operators", getattr(vendor_setup, 'VendorSetupOperatorsHandler')),
        (r"/vendors/([a-z0-9]*)/setup/insurances", getattr(vendor_setup, 'VendorSetupInsuranceListHandler')),
        (r"/vendors/([a-z0-9]*)/setup/insurances/create", getattr(vendor_setup, 'VendorSetupInsuranceCreateHandler')),
        (r"/vendors/([a-z0-9]*)/setup/insurances/([a-z0-9]*)/edit", getattr(vendor_setup, 'VendorSetupInsuranceEditHandler')),
        (r"/vendors/([a-z0-9]*)/setup/insurances/([a-z0-9]*)/delete", getattr(vendor_setup, 'VendorSetupInsuranceDeleteHandler')),
        (r"/vendors/([a-z0-9]*)/setup/wx", getattr(vendor_setup, 'VendorSetupWxHandler')),
        (r"/vendors/([a-z0-9]*)/setup/hha", getattr(vendor_setup, 'VendorSetupHhaHandler')),
        (r"/vendors/([a-z0-9]*)/setup/club", getattr(vendor_setup, 'VendorSetupClubHandler')),
        (r'/vendors/([a-z0-9]*)/setup/profile', getattr(vendor_setup, 'VendorProfileEditHandler')),
        (r'/vendors/([a-z0-9]*)/setup/binding-wx', getattr(vendor_setup, 'VendorBindingWxHandler')),

        # 任务
        (r'/vendors/([a-z0-9]*)/setup/task', getattr(vendor_setup, 'VendorSetupTaskHandler')),
        (r'/vendors/([a-z0-9]*)/setup/task/create', getattr(vendor_setup, 'VendorSetupTaskCreateHandler')),
        (r'/vendors/([a-z0-9]*)/setup/task/([a-z0-9]*)/allocate', getattr(vendor_setup, 'VendorSetupTaskAllocateHandler')),
        (r'/vendors/([a-z0-9]*)/setup/task/([a-z0-9]*)/delete', getattr(vendor_setup, 'VendorSetupTaskDeleteHandler')),

        # trip_router
        (r'/vendors/([a-z0-9]*)/trip_router', getattr(trip_router, 'VendorTriprouterListHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/create', getattr(trip_router, 'VendorTriprouterCreateHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/delete', getattr(trip_router, 'VendorTriprouterDeleteHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/edit/step1', getattr(trip_router, 'VendorTriprouterEditStep1Handler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/edit/step2', getattr(trip_router, 'VendorTriprouterEditStep2Handler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/clone', getattr(trip_router, 'VendorTriprouterCloneHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/activitylist', getattr(trip_router, 'VendorTriprouterActivityListHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/evallist', getattr(trip_router, 'VendorTriprouterEvalListHandler')),

        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/open/set', getattr(trip_router, 'VendorTriprouterOpenSetHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/open/cancel', getattr(trip_router, 'VendorTriprouterOpenCancelHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/share', getattr(trip_router, 'VendorTriprouterShareListHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/share/set', getattr(trip_router, 'VendorTriprouterShareSetHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/([a-z0-9]*)/share/cancel', getattr(trip_router, 'VendorTriprouterShareCancelHandler')),
        (r'/vendors/([a-z0-9]*)/trip_router/use', getattr(trip_router, 'VendorTriprouterUseListHandler')),


        # bike-forever ajax handler result
        (r"/bf/api/vendors/([a-z0-9]*)/categorys", getattr(api_category, 'ApiCategoryListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/activitys/popular", getattr(api_activity, 'ApiActivityPopularListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/activitys/completed", getattr(api_activity, 'ApiActivityCompletedListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)", getattr(api_activity, 'ApiActivityInfoXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/members", getattr(api_activity, 'ApiActivityMemberListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/share", getattr(api_activity, 'ApiActivityShareXHR')),


        (r"/bf/api/vendors/([a-z0-9]*)/orders", getattr(api_order, 'ApiOrdersXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/orders/activitys/([a-z0-9]*)", getattr(api_order, 'ApiActivityOrdersXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/orders/([a-z0-9]*)", getattr(api_order, 'ApiOrderInfoXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/orders/([a-z0-9]*)/review", getattr(api_order, 'ApiOrderReviewXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/orders/([a-z0-9]*)/delete", getattr(api_order, 'ApiOrderDeleteXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/order/search", getattr(api_order, 'ApiOrderSearchXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/voucher-orders", getattr(api_order, 'ApiVoucherOrderListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/voucher-orders/([a-z0-9]*)/review", getattr(api_order, 'ApiVoucherOrderReviewXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/apply/search", getattr(api_order, 'ApiApplySearchXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/applys", getattr(api_order, 'ApiApplyListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/applys/([a-z0-9]*)/review", getattr(api_order, 'ApiApplyReviewXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/activitys/([a-z0-9]*)/applys/export", getattr(api_order, 'ApiActivityExportXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/insurance-templates", getattr(api_setup, 'ApiSetupInsuranceTemplateListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/customer-profile/vouchers", getattr(api_customer_profile, 'ApiCustomerProfileVoucherListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/customer-profile/my", getattr(api_customer_profile, 'ApiCustomerProfileMyInfoXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/customer-profile/contacts", getattr(api_customer_profile, 'ApiCustomerProfileMyContactListXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/customers/([a-z0-9]*)/orders", getattr(api_customer_profile, 'ApiCustomerOrdersXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/customers/([a-z0-9]*)/points", getattr(api_customer_profile, 'ApiCustomerPointsXHR')),
        (r"/bf/api/vendors/([a-z0-9]*)/customer-profile/customers", getattr(api_customer_profile, 'ApiCustomerListXHR')),
        (r"/bf/api/leagues/([a-z0-9]*)/apply-cashout/([a-z0-9]*)/review", getattr(api_order, 'ApiApplyCashoutReviewXHR')),

        # comm
        ('.*', getattr(comm, 'PageNotFoundHandler'))

    ]

    return config
