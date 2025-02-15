from app.models import Role, ContractStatus

users = [
    [
        "Elladine Staterfield",
        "estaterfield0@nsw.gov.au",
        "1301924404",
        Role.SALES,
        "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433",
    ],
    [
        "Gare Wealthall",
        "gwealthall1@indiegogo.com",
        "1072455114",
        Role.SUPPORT,
        "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433",
    ],
    [
        "Querida Santer",
        "qsanterh@plala.or.jp",
        "4715820827",
        Role.ADMIN,
        "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433",
    ],
    [
        "Seth Mossman",
        "smossman3@miibeian.gov.cn",
        "1244349758",
        Role.ADMIN,
        "scrypt:32768:8:1$OFgFJ0hJU9srVuTx$1b2ff4574cd389274249130b15639f63fb23b7d86aff85d73268ab62c1f3b81e7c884890df41bcd83ca459eff0cbcd9854e52356557a265e4c57d6d7f0c17433",
    ],
]

clients = [
    [
        "Gilburt Scarf",
        "gscarf0@tuttocitta.it",
        "6195732158",
        "Schulist-Hayes",
        1,
    ],
    [
        "Rebeka Asken",
        "rasken1@tuttocitta.it",
        "4702503993",
        "Pfeffer, Murphy and Cronin",
        4,
    ],
    [
        "Tamra Aiskrigg",
        "taiskrigg2@mediafire.com",
        "8139795596",
        "Feest-Pollich",
        1,
    ],
    [
        "Lane Elener",
        "lelener3@wired.com",
        "7051969850",
        "Heller-Becker",
        1,
    ],
    [
        "Mano Rohlf",
        "mrohlf4@liveinternet.ru",
        "6074872496",
        "Swaniawski Group",
        1,
    ],
]

contracts = [
    [1, 1, 4432.93, 1486.28, ContractStatus.SIGNED],
    [2, 4, 802.91, 4868.02, ContractStatus.SIGNED],
    [3, 1, 1603.67, 4283.48, ContractStatus.PENDING],
    [4, 1, 2629.66, 1337.22, ContractStatus.PENDING],
    [5, 1, 3465.32, 374.14, ContractStatus.PENDING],
]
