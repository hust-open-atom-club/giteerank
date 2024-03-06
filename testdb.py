from gitee_ranking.schema import Base, Class, ClassMember, Group, SessionLocal, engine

Base.metadata.create_all(engine)

session = SessionLocal()

# new_class = Class(name="信安2102班")

# session.add(new_class)
# session.flush()

# # for name in ["A", "B", "C", "D"]:
# for name in ['A', 'B', 'C', 'D', 'E']:
#     session.add(Group(name=name, class_id=new_class.id))

# session.commit()

import pandas as pd

df = pd.read_csv("data/xinan2102.csv")

for index, row in df.iterrows():
    group_name = row["group_name"]
    name = row["name"]
    email = row["email"]

    group = (
        session.query(Group)
        .join(Class)
        .filter(
            Class.id == Group.class_id,
            Group.name == group_name,
            Class.name == "信安2102班",
        )
        .first()
    )
    if not group:
        print(f"Group {group_name} not found")
        continue

    print(f"Adding {name} {email} to {group_name}")
    member = ClassMember(
        name=name, email=email, class_id=group.class_id, group_id=group.id
    )

    session.add(member)

session.commit()
session.close()
