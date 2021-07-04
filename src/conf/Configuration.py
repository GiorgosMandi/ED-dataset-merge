# ALL ACE'S EVENT TYPES
# LIFE.BE-BORN
# LIFE.MARRY
# LIFE.DIVORCE
# LIFE.INJURE
# LIFE.DIE
# MOVEMENT.TRANSPORT
# TRANSACTION.TRANSFER-OWNERSHIP
# TRANSACTION.TRANSFER-MONEY
# BUSINESS.START-ORG
# BUSINESS.MERGE-ORG
# BUSINESS.DECLARE-BANKRUPTCY
# BUSINESS.END-ORG
# CONFLICT.ATTACK
# CONFLICT.DEMONSTRATE
# CONTACT.MEET
# CONTACT.PHONE-WRITE
# PERSONELL.START-POSITION
# PERSONELL.END-POSITION
# PERSONELL.NOMINATE
# PERSONELL.ELECT
# JUSTICE.ARREST-JAIL
# JUSTICE.RELEASE-PAROLE
# JUSTICE.TRIAL-HEARING
# JUSTICE.CHARGE-INDICT
# JUSTICE.SUE
# JUSTICE.CONVICT
# JUSTICE.SENTENCE
# JUSTICE.FINE
# JUSTICE.EXECUTE
# JUSTICE.EXTRADITE
# JUSTICE.ACQUIT
# JUSTICE.APPEAL
# JUSTICE.PARDON


events_mapping = {

    "LIFE.BE-BORN": "LIFE.BE-BORN",
    "LIFE.MARRY": "LIFE.MARRY",
    "LIFE.DIVORCE": "LIFE.DIVORCE",
    "LIFE.INJURE": "LIFE.INJURE",
    "LIFE.DIE": "LIFE.DIE",

    "MOVEMENT.TRANSPORT": "MOVEMENT.TRANSPORT",

    "TRANSACTION.TRANSFER-OWNERSHIP": "TRANSACTION.TRANSFER-OWNERSHIP",
    "TRANSACTION.TRANSFER-MONEY": "TRANSACTION.TRANSFER-MONEY",

    "BUSINESS.START-ORG": "BUSINESS.START-ORG",
    "BUSINESS.MERGE-ORG": "BUSINESS.MERGE-ORG",
    "BUSINESS.DECLARE-BANKRUPTCY": "BUSINESS.DECLARE-BANKRUPTCY",
    "BUSINESS.END-ORG": "BUSINESS.END-ORG",

    "CONFLICT.ATTACK": "CONFLICT.ATTACK",
    "CONFLICT.DEMONSTRATE": "CONFLICT.DEMONSTRATE",

    "CONTACT.MEET": "CONTACT.MEET",
    "CONTACT.PHONE-WRITE": "CONTACT.PHONE-WRITE",

    # there is a typo in the documentation of ACE pdf - I don't know if also exists in the dataset
    "PERSONELL.START-POSITION": "PERSONNEL.START-POSITION",
    "PERSONELL.END-POSITION": "PERSONNEL.END-POSITION",
    "PERSONELL.NOMINATE": "PERSONNEL.NOMINATE",
    "PERSONELL.ELECT": "PERSONNEL.ELECT",
    "PERSONNEL.START-POSITION": "PERSONNEL.START-POSITION",
    "PERSONNEL.END-POSITION": "PERSONNEL.END-POSITION",
    "PERSONNEL.NOMINATE": "PERSONNEL.NOMINATE",
    "PERSONNEL.ELECT": "PERSONNEL.ELECT",

    "JUSTICE.ARREST-JAIL": "JUSTICE.ARREST-JAIL",
    "JUSTICE.RELEASE-PAROLE": "JUSTICE.RELEASE-PAROLE",
    "JUSTICE.TRIAL-HEARING": "JUSTICE.TRIAL-HEARING",
    "JUSTICE.CHARGE-INDICT": "JUSTICE.CHARGE-INDICT",
    "JUSTICE.SUE": "JUSTICE.SUE",
    "JUSTICE.CONVICT": "JUSTICE.CONVICT",
    "JUSTICE.SENTENCE": "JUSTICE.SENTENCE",
    "JUSTICE.FINE": "JUSTICE.FINE",
    "JUSTICE.EXECUTE": "JUSTICE.EXECUTE",
    "JUSTICE.EXTRADITE": "JUSTICE.EXTRADITE",
    "JUSTICE.ACQUIT": "JUSTICE.ACQUIT",
    "JUSTICE.APPEAL": "JUSTICE.APPEAL",
    "JUSTICE.PARDON": "JUSTICE.PARDON",

    "Justice:Arrest-Jail": "JUSTICE.ARREST-JAIL",
    "Life:Die": "LIFE.DIE",
    "Conflict:Attack": "CONFLICT.ATTACK",
    "Transaction:Transfer-Money": "TRANSACTION.TRANSFER-MONEY",
    "Conflict:Demonstrate": "CONFLICT.DEMONSTRATE",
    "Contact:Phone-Write": "CONTACT.PHONE-WRITE",
    "Contact:Meet": "CONTACT.MEET",
    "Movement:Transport": "MOVEMENT.TRANSPORT",

    "property seizure/destruction": "ARTIFACT.DESTRUCTION",
    "fight": "CONFLICT.ATTACK",
    "release people": "JUSTICE.RELEASE-PAROLE",
    "protest/riot": "CONFLICT.DEMONSTRATE",
    "terrorist/suicide attack": "CONFLICT.ATTACK",
    "exhibit force posture": "CONFLICT.ATTACK",
    "assault": "CONFLICT.ATTACK",
    "cyber attack": "CONFLICT.ATTACK",
    "restrict/reduce rights": "JUSTICE.CHARGE-INDICT",
    "arrest": "JUSTICE.ARREST",

    "contact.commandorder.correspondence": "CONTACT.MEET",
    "contact.requestadvise.correspondence": "CONTACT.MEET",
    "contact.discussion.n/a": "CONTACT.MEET",
    "contact.commandorder.broadcast": "CONTACT",
    "contact.prevarication.broadcast": "CONTACT",
    "contact.discussion.meet": "CONTACT.MEET",
    "contact.negotiate.meet": "CONTACT.MEET",
    "contact.commitmentpromiseexpressintent.n/a": "CONTACT.EXPRESS-INTENT",
    "contact.commitmentpromiseexpressintent.broadcast": "CONTACT.EXPRESS-INTENT",
    "contact.commitmentpromiseexpressintent.correspondence": "CONTACT.EXPRESS-INTENT",
    "contact.requestadvise.broadcast": "CONTACT",
    "contact.mediastatement.broadcast": "CONTACT",
    "contact.threatencoerce.n/a": "CONTACT",
    "contact.negotiate.n/a": "CONTACT",
    "contact.collaborate.n/a": "CONTACT",
    "contact.collaborate.correspondence": "CONTACT",

    "contact.commitmentpromiseexpressintent.meet": "CONTACT.MEET",
    "life.injure.illnessdegradationhungerthirst": "LIFE.INJURE",
    "life.die.deathcausedbyviolentevents": "LIFE.DIE",
    "life.injure.n/a": "LIFE.INJURE",
    "life.injure.injurycausedbyviolentevents": "LIFE.INJURE",
    "life.injure.illnessdegradationphysical": "LIFE.INJURE",

    "conflict.attack.stealrobhijack": "CONFLICT.ATTACK",
    "conflict.attack.firearmattack": "CONFLICT.ATTACK",
    "conflict.attack.stabbing": "CONFLICT.ATTACK",
    "conflict.attack.airstrikemissilestrike": "CONFLICT.ATTACK",
    "conflict.attack.selfdirectedbattle": "CONFLICT.ATTACK",
    "conflict.yield.retreat": "CONFLICT.RETREAT",

    "movement.transportperson.prevententry": "MOVEMENT.TRANSPORT",
    "movement.transportperson.hide": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.disperseseparate": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.smuggleextract": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.nonviolentthrowlaunch": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.hide": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.sendsupplyexport": "MOVEMENT.TRANSPORT",
    "movement.transportperson.preventexit": "MOVEMENT.TRANSPORT",

    "justice.initiatejudicialprocess.trialhearing": "JUSTICE.TRIAL-HEARING",
    "justice.initiatejudicialprocess.n/a": "JUSTICE.TRIAL-HEARING",
    "justice.judicialconsequences.n/a": "JUSTICE.SENTENCE",
    "justice.arrestjaildetain.arrestjaildetain": "JUSTICE.ARREST-JAIL",
    "justice.judicialconsequences.execute": "JUSTICE.EXECUTE",
    "justice.judicialconsequences.extradite": "JUSTICE.EXTRADITE",
    "justice.investigate.n/a": "JUSTICE.INVESTIGATE",
    "justice.investigate.investigatecrime": "JUSTICE.INVESTIGATE",

    "transaction.transferownership.n/a": "TRANSACTION.TRANSFER-OWNERSHIP",
    "transaction.transfermoney.giftgrantprovideaid": "TRANSACTION.TRANSFER-MONEY",
    "transaction.transfermoney.n/a": "TRANSACTION.TRANSFER-MONEY",
    "transaction.transfermoney.embargosanction": "TRANSACTION.TRANSFER-MONEY",
    "transaction.transfermoney.purchase": "TRANSACTION.TRANSFER-MONEY",
    "transaction.transaction.transfercontrol": "TRANSACTION.TRANSFER-OWNERSHIP",

    "personnel.elect.n/a": "PERSONNEL.ELECT",
    "personnel.endposition.firinglayoff": "PERSONNEL.END-POSITION",
    "personnel.endposition.n/a": "PERSONNEL.END-POSITION",

    "government.agreements.n/a": "GPE.AGREEMENT",
    "government.legislate.legislate": "GPE.GOVERNMENT-LEGISLATE",
    "government.agreements.acceptagreementcontractceasefire": "GPE.AGREEMENT",
    "government.formation.n/a": "GPE.GOVERNMENT-FORMATION",
    "government.spy.spy": "GPE.SPY",
    "government.vote.violationspreventvote": "GPE.VOTE",
    "government.agreements.violateagreement": "GPE.AGREEMENT",
    "transaction.transaction.embargosanction": "GPE.SACTIONS",

    "disaster.fireexplosion.fireexplosion": "ARTIFACT.DESTRUCTION",
    "manufacture.artifact.build": "ARTIFACT.CONSTRUCTION",
    "inspection.sensoryobserve.n/a": "INSPECTION",

    "contact.threatencoerce.meet": "CONTACT.MEET",
    "contact.requestadvise.meet": "CONTACT.MEET",
    "contact.prevarication.correspondence": "CONTACT",
    "contact.publicstatementinperson.n/a": "CONTACT",
    "contact.negotiate.correspondence": "CONTACT",
    "contact.threatencoerce.broadcast": "CONTACT",
    "contact.requestadvise.n/a": "CONTACT",
    "contact.discussion.correspondence": "CONTACT",
    "contact.prevarication.n/a": "CONTACT",
    "contact.commandorder.n/a": "CONTACT",
    "contact.collaborate.meet": "CONTACT",
    "contact.funeralvigil.n/a": "CONTACT",
    "contact.prevarication.meet": "CONTACT.MEET",
    "contact.threatencoerce.correspondence": "CONTACT",
    "contact.publicstatementinperson.broadcast": "CONTACT",
    "contact.funeralvigil.meet": "CONTACT",
    "contact.mediastatement.n/a": "CONTACT",
    "contact.commandorder.meet": "CONTACT.MEET",
    "conflict.attack.n/a": "CONFLICT.ATTACK",
    "conflict.attack.biologicalchemicalpoisonattack": "CONFLICT.ATTACK",
    "conflict.yield.surrender": "CONFLICT.RETREAT",
    "conflict.demonstrate.marchprotestpoliticalgathering": "CONFLICT.DEMONSTRATE",
    "conflict.yield.n/a": "CONFLICT",
    "conflict.demonstrate.n/a": "CONFLICT.DEMONSTRATE",
    "conflict.attack.bombing": "CONFLICT.ATTACK",
    "conflict.attack.hanging": "CONFLICT.ATTACK",
    "conflict.attack.invade": "CONFLICT.ATTACK",
    "conflict.attack.setfire": "CONFLICT.ATTACK",
    "conflict.attack.strangling": "CONFLICT.ATTACK",
    "movement.transportperson.smuggleextract": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.n/a": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.fall": "MOVEMENT.TRANSPORT",
    "movement.transportperson.selfmotion": "MOVEMENT.TRANSPORT",
    "movement.transportperson.grantentryasylum": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.bringcarryunload": "MOVEMENT.TRANSPORT",
    "movement.transportperson.n/a": "MOVEMENT.TRANSPORT",
    "movement.transportperson.evacuationrescue": "MOVEMENT.TRANSPORT",
    "movement.transportperson.fall": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.grantentry": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.receiveimport": "MOVEMENT.TRANSPORT",
    "movement.transportperson.disperseseparate": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.prevententry": "MOVEMENT.TRANSPORT",
    "movement.transportartifact.preventexit": "MOVEMENT.TRANSPORT",
    "movement.transportperson.bringcarryunload": "MOVEMENT.TRANSPORT",
    "transaction.transaction.n/a": "TRANSACTION",
    "transaction.transfermoney.payforservice": "TRANSACTION.TRANSFER-MONEY",
    "transaction.transferownership.embargosanction": "TRANSACTION.TRANSFER-OWNERSHIP",
    "transaction.transferownership.giftgrantprovideaid": "TRANSACTION.TRANSFER-OWNERSHIP",
    "transaction.transferownership.purchase": "TRANSACTION.TRANSFER-OWNERSHIP",
    "transaction.transferownership.borrowlend": "TRANSACTION.TRANSFER-OWNERSHIP",
    "transaction.transaction.giftgrantprovideaid": "TRANSACTION",
    "transaction.transfermoney.borrowlend": "TRANSACTION.TRANSFER-MONEY",
    "government.formation.mergegpe": "GPE.GOVERNMENT-FORMATION",
    "government.agreements.rejectnullifyagreementcontractceasefire": "GPE.AGREEMENT",
    "government.vote.n/a": "GPE.VOTE",
    "government.formation.startgpe": "GPE.GOVERNMENT-FORMATION",
    "government.vote.castvote": "GPE.VOTE",
    "justice.judicialconsequences.convict": "JUSTICE.SENTENCE",
    "justice.initiatejudicialprocess.chargeindict": "JUSTICE.CHARGE-INDICT",
    "manufacture.artifact.n/a": "ARTIFACT.CONSTRUCTION",
    "artifactexistence.damagedestroy.destroy": "ARTIFACT.DESTRUCTION",
    "artifactexistence.damagedestroy.damage": "ARTIFACT.DESTRUCTION",
    "manufacture.artifact.createmanufacture": "ARTIFACT.CONSTRUCTION",
    "artifactexistence.damagedestroy.n/a": "ARTIFACT.DESTRUCTION",
    "manufacture.artifact.createintellectualproperty": "ARTIFACT.CONSTRUCTION",
    "inspection.sensoryobserve.inspectpeopleorganization": "INSPECTION",
    "inspection.sensoryobserve.monitorelection": "INSPECTION",
    "inspection.sensoryobserve.physicalinvestigateinspect": "INSPECTION",
    "personnel.startposition.n/a": "PERSONNEL.START-POSITION",
    "personnel.elect.winelection": "PERSONNEL.ELECT",
    "personnel.startposition.hiring": "PERSONNEL.START-POSITION",
    "personnel.endposition.quitretire": "PERSONNEL.END-POSITION",
    "life.die.n/a": "LIFE.DIE",
    "life.die.nonviolentdeath": "LIFE.DIE",
    "disaster.accidentcrash.accidentcrash": "DISASTER"

}

events = list(set(events_mapping.values()))

roles_mapping = {
    "police": "police",
    "person": "person",
    "agent": "agent",
    "entity": "observedentity",
    "communicator": "communicator",
    "transporter": "transporter",
    "recipient": "recipient",
    "judgecourt": "judgecourt",
    "target": "target",
    "otherparticipant": "otherparticipant",
    "defendant": "defendant",
    "observedentity": "observedentity",
    "place": "place",
    "killer": "killer",
    "investigator": "investigator",
    "artifact": "artifact",
    "detainee": "detainee",
    "prosecutor": "prosecutor",
    "executioner": "executioner",
    "beneficiary": "beneficiary",
    "passenger": "passenger",
    "preventer": "preventer",
    "participant": "participant",
    "candidate": "candidate",
    "victim": "victim",
    "spy": "spy",
    "attacker": "attacker",
    "money": "money",
    "jailer": "jailer",
    "fireexplosionobject": "fireexplosionobject",
    "instrument": "instrument",
    "extraditer": "extraditer",
    "giver": "giver",
    "governmentbody": "governmentbody",
    "employee": "employee",
    "injurer": "injurer",
    "observer": "observer",
    "crime": "crime",
    "violator": "violator",
    "destination": "destination",
    "origin": "origin",
    "retreater": "retreater",
    "manufacturer": "manufacturer",
    "placeofemployment": "placeofemployment",
    "vehicle": "vehicle",
    "arrested": "arrested",
    "property": "property",
    "location": "place",
    "location adverb": "place",
    "weapons": "instrument",
    "aim": "aim",
    "perpetrator": "perpetrator",
    "time": "time",
    "injured": "injured",
    "kidnapped": "kidnapped",
    "displaced": "displaced",
    "dead": "dead",
    "indirect participant": "participant",
    "num dead": "numberofaffected",
    "num injured": "numberofaffected",
    "num displaced": "numberofaffected",
    "num kidnapped": "numberofaffected",
    "num arrested": "numberofaffected",

    "surrenderer": "surrenderer",
    "monitor": "monitor",
    "inspectedentity": "inspectedentity",
    "founder": "founder",
    "ballot": "ballot",
    "crashobject": "crashobject",
    "gpe": "gpe",
    "voter": "voter",
    "inspector": "inspector",
    "rejecternullifier": "rejecternullifier",
    "monitoredentity": "monitoredentity",
    "driverpassenger": "driverpassenger",
    "result": "result",
    "territoryorfacility": "territoryorfacility",
    "hidingplace": "hidingplace",
    "damager": "damager",
    "yielder": "yielder",
    "granter": "granter",
    "artifactmoney": "artifactmoney",
    "destroyer": "destroyer",
    "damagerdestroyer": "damagerdestroyer",
    "law": "law",
    "deceased": "deceased",
    "demonstrator": "demonstrator"
}

roles = list(set(roles_mapping.values()))
