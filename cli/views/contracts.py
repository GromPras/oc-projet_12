from rich.console import Console
from rich.table import Table
from cli.helpers import format_phone


def contracts_list_view(contracts):
    # id: Mapped[int] = mapped_column(primary_key=True)
    # client_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("client.id"))
    # client: Mapped["Client"] = relationship(back_populates="contracts")
    # sales_contact_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("user.id"))
    # sales_contact: Mapped["User"] = relationship(
    #     back_populates="contracts", foreign_keys=[sales_contact_id]
    # )
    # total_amount: Mapped[float] = mapped_column(sa.Float)
    # remaining_amount: Mapped[float] = mapped_column(sa.Float)
    # status: Mapped[ContractStatus] = mapped_column(default=ContractStatus.PENDING)
    # created_at: Mapped[datetime] = mapped_column(
    #     default=lambda: datetime.now(timezone.utc)
    # )
    # updated_at: Mapped[datetime] = mapped_column(
    #     default=lambda: datetime.now(timezone.utc)
    # )
    # events: Mapped[Optional[List["Event"]]] = relationship(back_populates="contract")

    table = Table(title="Contracts")
    table.add_column("ID")
    table.add_column("Client")
    table.add_column("Sales Rep")
    table.add_column("Total")
    table.add_column("Due")
    table.add_column("Status")

    for contract in contracts:
        table.add_row(
            str(contract["id"]),
            str(contract["client"]["fullname"]),
            str(contract["sales_contact"]["fullname"]),
            str(contract["total_amount"]),
            str(contract["remaining_amount"]),
            str(contract["status"]),
        )

    console = Console()
    console.print(table)
