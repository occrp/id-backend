
CREATE INDEX ON :UKCompany(uk_cs_id)
CREATE INDEX ON :UKPerson(uk_cs_pnr)

// ==> cs_uk_directors.csv <==
// version,hns,suf,mname,dob,trp02,pnr,title,ptitle,fname,sname

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
CREATE (person:LegalPerson:Person:UKPerson {
    uk_cs_pnr: csvLine.pnr,
    dob: csvLine.dob,
    first_name: csvLine.fname,
    middle_names: csvLine.mname,
    last_name: csvLine.sname,
    name_honours: csvLine.hns,
    name_suffix: csvLine.suf,
    title: csvLine.title
})
;

// ==> cs_uk_companies.csv <==
// version,sic07desc,tradpost,sic07,inc,name,aorder,add2,
// trad2,add1,trad1,add4,trad4,trp01,org,add3,trad3,descr,
// rec_status,web,stat,type,volag,dissdate,acc_type,post,
// admin,liq_status,charnum

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
CREATE (company:LegalPerson:Company:UKCompany {
    name: csvLine.name,
    incorporation_date: csvLine.inc,
    dissolution_date: csvLine.dissdate,
    is_liquidated: csvLine.liq_status,
    in_receivership: csvLine.rec_status,

    uk_cs_id: csvLine.org,

})
CREATE UNIQUE (sic07:SIC07 {
    sic07code: csvLine.sic07,
    description: csvLine.sic07code
})
CREATE UNIQUE (regaddress:Address {
    addr1: csvLine.trad1,
    addr2: csvLine.trad2,
    addr3: csvLine.trad3,
    addr4: csvLine.trad4,
    postcode: csvline.tradpost
})
CREATE UNIQUE (mainaddress:Address {
    addr1: csvLine.trad1,
    addr2: csvLine.trad2,
    addr3: csvLine.trad3,
    addr4: csvLine.trad4,
    postcode: csvline.tradpost
})
CREATE (company)-[:registered_at]->(regaddress)
CREATE UNIQUE (company)-[:has_address]->(regaddress)
CREATE UNIQUE (company)-[:main_address]->(regaddress)
CREATE (company)-[:sic07code]->(sic07)
CREATE (company)-[:website]->(Website: {
    url: csvLine.web,
})

// ==> cs_uk_trading_addresses.csv <==
// version,_id,tradpost,trad1,trad4,tel,td001,org,tps,trad2,trad3

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (c:Country {iso:"UK"})
MERGE (company:UKCompany {uk_cs_id: csvLine.org})
CREATE UNIQUE (address:Address {
    addr1: csvLine.trad1,
    addr2: csvLine.trad2,
    addr3: csvLine.trad3,
    addr4: csvLine.trad4,
    postcode: csvline.tradpost,
})
CREATE UNIQUE (company)-[:has_address]->(address)
CREATE UNIQUE (address)-[:is_in]->(c)
CREATE UNIQUE (telephone:PhoneNumber) {
    number: csvLine.tel
})
CREATE (company)-[:has_phonenumber]->(telephone)
;


// ==> cs_uk_company_accounts.csv <==
// version,tangas,audqual,netwrth,stock,nomon,taxation,date,incincsh,sunrese,placcres,trdebt,contliab,liabcurr,asstotfix,netass,grprof,ptaxpro,ltloan,diremol,netcsfrfn,trp04,capemp,accname,liabmisccur,totliab,asstotcur,cstsales,wrkcap,liablt,netcsbffn,proaftax,org,intpay,intass,exports,curr,bnkovr,retpro,audfee,depre,numemp,audname,acctype,revres,opprof,bnkovltln,shrttrmlns,paidupeq,asscur,trover,accformat,asstot,acstat,wages,trcred,divpay,opnetcashf,consol,shrfun,solname,assothcur

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:%PATH%" as csvLine
MERGE (company:UKCompany {uk_cs_id: csvLine.org})
CREATE (cr:CompanyRecord:UKCompanyRecord {
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
CREATE (solicitor:Person:LegalPerson:Solicitor {
    name:   csvLine.solname,
})
CREATE (auditor:Person:LegalPerson:Auditor {
    name:   csvLine.audname,
    auditor_qualification_code: csvLine.audqual,
})
CREATE (accountant:Person:LegalPerson:Accountant {
    name:   csvLine.accname,
})
CREATE (solicitor)-[:solicitor_for]->(company)
CREATE (accountant)-[:accounted]->(cr)
CREATE (accountant)-[:accountant_for]->(company)
CREATE (auditor)-[:created_audit {price: csvLine.audfee}]->(cr)
CREATE (auditor)-[:audited]->(company)
;

// ==> cs_uk_directorships.csv <==
// version,poscode,resdate_str,func,pnr,trp03,org,funcode,pos,sec,active,resdate,appdate,id


// ==> cs_uk_group_structure.csv <==
// version,gs002,regnum,safenum,name,holdnum,level,org,kfin,ultholdnum

