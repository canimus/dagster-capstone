import dagster as dg

country_partition = dg.StaticPartitionsDefinition(
    partition_keys="AD,AL,AT,BE,BG,BY,CH,CZ,DE,EE,ES,FR,HR,HU,IE,IT,LI,LT,LU,LV,MC,MD,MT,NL,PL,PT,RO,RS,SE,SI,SK,SM,VA".split(
        ","
    )
)

yearly_partition = dg.StaticPartitionsDefinition(
    partition_keys=list(map(str, range(2020, 2026)))
)

monthly_partition = dg.MonthlyPartitionsDefinition(start_date="2020-01-01")

dimensional_partition = dg.MultiPartitionsDefinition(
    partitions_defs={"country": country_partition, "month": monthly_partition}
)

summary_partition = dg.MultiPartitionsDefinition(
    partitions_defs={"country": country_partition, "year": yearly_partition}
)
