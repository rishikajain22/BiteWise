import seaborn as sns
import pandas as pd
import matplotlib.pylot as plt
data = {
    "Department": ["CSE","CSE","ECE","ECE","ME","ME"],
    "Salary": [50000,90000,45000,47000,40000,95000]
}
df = pd.DataFrame(data)
sns.boxplot(x="Department", y="Salary", data=df )
plt.title("Salary Distribution by Department")
plt.show()