// ==> cs_uk_company_accounts.csv <==
// version,tangas,audqual,netwrth,stock,nomon,taxation,date,incincsh,sunrese,placcres,trdebt,contliab,liabcurr,asstotfix,netass,grprof,ptaxpro,ltloan,diremol,netcsfrfn,trp04,capemp,accname,liabmisccur,totliab,asstotcur,cstsales,wrkcap,liablt,netcsbffn,proaftax,org,intpay,intass,exports,curr,bnkovr,retpro,audfee,depre,numemp,audname,acctype,revres,opprof,bnkovltln,shrttrmlns,paidupeq,asscur,trover,accformat,asstot,acstat,wages,trcred,divpay,opnetcashf,consol,shrfun,solname,assothcur

USING PERIODIC COMMIT 100
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (company:UKCompany {uk_cs_id: csvLine.org})
CREATE (cr:CompanyRecord:UKCompanyRecord:CompaniesHouseData {
    date:                   csvLine.date
    accounts_format:        csvLine.accformat
    tangible_assets:        csvLine.tangas,
    netwrth:                csvLine.netwrth,
    stock:                  csvLine.stock,
    number_of_months:       csvLine.nomon,
    taxation:               csvLine.taxation,
    increase_in_cash:       csvLine.incincsh,
    sundry_reserves:        csvLine.sunrese,
    pl_accout_reserves:     csvLine.placcres,
    trade_debtors:          csvLine.trdebt,
    trade_creditors:        csvLine.trcred,
    liabilities_contingent: csvLine.contliab,
    liabilities_current:    csvLine.liabcurr,
    liabilities_long_term:  csvLine.liablt,
    liabilities_misc_current:   csvLine.liabmisccur,
    liabilities_total:      csvLine.totliab,
    assets_current:         csvLine.asscur,
    assets_fixed_total:     csvLine.asstotfix,
    assets_intangible:      csvLine.intass,
    assets_other_current:   csvLine.assothcur
    assets_net:             csvLine.netass,
    assets_total:           csvLine.asstot,
    profits_gross:          csvLine.grprof,
    profits_before_tax:     csvLine.ptaxpro,
    profits_after_tax:      csvLine.proaftax,
    profits_operating:      csvLine.opprof,
    profits_retained:       csvLine.retpro,
    loans_long_term:        csvLine.ltloan,
    loans_short_term:       csvLine.shrttrmlns,
    bank_overdraft:         csvLine.bnkovr,
    bank_overdraft_and_long_term_loans:   csvLine.bnkovltln,
    director_emoluments:    csvLine.diremol,
    cashflow_net_from_financing:   csvLine.netcsfrfn,
    cashflow_net_before_financing: csvLine.netcsbffn,
    capital_employed:       csvLine.capemp,
    assets_total_current:   csvLine.asstotcur,
    cost_of_sales:          csvLine.cstsales,
    working_capital:        csvLine.wrkcap,
    interest_payments:      csvLine.intpay,
    exports:                csvLine.exports,
    currency:               csvLine.curr,
    depreciation:           csvLine.depre,
    employees_number:       csvLine.numemp,
    accounts_type:          csvLine.acctype,
    accounts_format:        csvLine.accformat,
    accounts_status:        csvLine.acstat,
    revaluation_reserve:    csvLine.revres,
    paid_up_equity:         csvLine.paidupeq,
    turnover:               csvLine.trover,
    wages:                  csvLine.wages,
    dividends_payable:      csvLine.divpay,
    operations_net_cashflow:csvLine.opnetcashf,
    consolidated_accounts:  csvLine.consol,
    shareholder_funds:      csvLine.shrfun,
})
CREATE UNIQUE (solicitor:Person {
    name:   csvLine.solname,
})
SET solicitor :LegalPerson:Solicitor:CompaniesHouseData
CREATE UNIQUE (auditor:Person {
    name:   csvLine.audname,
    auditor_qualification_code: csvLine.audqual,
})
SET auditor :LegalPerson:Auditor:CompaniesHouseData
CREATE UNIQUE (accountant:Person {
    name:   csvLine.accname,
})
SET accountant :LegalPerson:Accountant:CompaniesHouseData
CREATE (solicitor)-[:solicitor_for]->(company)
CREATE (accountant)-[:accounted]->(cr)
CREATE (accountant)-[:accountant_for]->(company)
CREATE (auditor)-[:created_audit {price: csvLine.audfee}]->(cr)
CREATE (auditor)-[:audited]->(company)
;