import pandas as pd
#from queue import Queue


def chenge(x):
    if x == 'H':
        return int(3)
    elif x == 'M':
        return int(2)
    elif x == 'L':
        return int(1)
    else:
        return int(0)

class TreeNode:
    def __init__(self, id, contribution, evaluation):
        self.id = id
        self.contribution = contribution
        self.evaluation = evaluation
        self.children = []
        self.parent = None

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self
    def is_leaf(self):
        return len(self.children) == 0
def print_tree(node, indent=""):
    if node is None:
        return  # ノードがNoneの場合は再帰を終了する
    print(f"{indent}ID: {node.id}, 貢献度: {node.contribution}, 評価点: {node.evaluation}")
    for child in node.children:
        print_tree(child, indent + "  ")


    
# Excelファイルから木構造を作成する関数
def create_tree_from_excel(excel_file, architecture_sheet_name, request_sheet_name, parent_node_value, parent_node=None):
    architecture_df = pd.read_excel(excel_file, sheet_name=architecture_sheet_name)
    request_df = pd.read_excel(excel_file, sheet_name=request_sheet_name)

    child_nodes_df = architecture_df[architecture_df['親'] == parent_node_value]

    if parent_node is None:
        parent_node = TreeNode(parent_node_value, 1, 0)

    for index, row in child_nodes_df.iterrows():
        if row['親'] == parent_node_value :
            id = row['実現手法']
            contribution = chenge(row['貢献度'])
            child_value = row['実現手法']
            child_evaluation = request_df.loc[request_df['名称'] == child_value, '目標値'].values
            if len(child_evaluation) > 0:
                child_evaluation = child_evaluation[0]
            else:
                child_evaluation = default_evaluation_value  # デフォルトの評価値を設定する
            node = TreeNode(id, contribution, child_evaluation+1.0)
            # create_tree_from_excel関数内の適切な位置に以下のデバッグステートメントを追加
            parent_node.add_child(node)
            create_tree_from_excel(excel_file, architecture_sheet_name, request_sheet_name, id, node)  # 修正点：引数からnodeを削除

    # requestのシートからも子ノードを探して追加する
    for index, row in request_df.iterrows():
        if row['親'] == parent_node_value :
            id = row['名称']
            contribution = chenge(row['貢献度'])
            child_value = row['名称']
            child_evaluation = row['目標値']
            node = TreeNode(id, contribution, child_evaluation)
            if parent_node is None:
                parent_node = node
            else:
                parent_node.add_child(node)
            # 再帰的に子ノードを探し、追加する
            create_tree_from_excel(excel_file, architecture_sheet_name, request_sheet_name, id, node)  

    return parent_node

def remove_zero_contribution(node):
    if node is None:
        return None
    
    updated_children = []
    
    # 子ノードの貢献度が0でないもの、または子ノードがない場合を抽出
    for child in node.children:
        updated_child = remove_zero_contribution(child)
        if updated_child and updated_child.contribution != 0:
            updated_children.append(updated_child)
        else:
            if updated_child:
                for grandchild in updated_child.children:
                    node.add_child(grandchild)  # 親の親ノードとの関係を修正

    node.children = updated_children
    
    # 貢献度が0の親ノードを削除し、その子ノードを親の親ノードに関連付ける
    if node.contribution == 0 and not any(child.contribution != 0 for child in node.children):
        return None
    else:
        return node





excel_file = "テストと_保守性_DB.xlsx"    # Excelファイルのパスを指定
architecture_sheet_name = "architecture"  # architectureシートの名前
request_sheet_name = "request"  # requestシートの名前
root_node_id = "モジュール性"  # ルートノードのIDを指定
default_evaluation_value = 0  # デフォルトの評価値を設定
       

# ツリー構造の作成
root_node = create_tree_from_excel(excel_file, architecture_sheet_name, request_sheet_name, root_node_id)
# 与えられたツリーのルートノードを取得して削除関数を適用
#root_node = create_tree_from_excel(excel_file, architecture_sheet_name, request_sheet_name, root_value)
updated_root = remove_zero_contribution(root_node)
# 更新されたツリーの表示
print("更新されたツリー:")
print_tree(updated_root)
#print_tree(root_node)

def calculate_achievement(node):
    if node.is_leaf():
        # 葉ノードの場合、達成度は自身の評価点と貢献度の積
        return node.evaluation *100
    else:
        # 子ノードの達成度と貢献度を考慮して親ノードの達成度を計算
        total_numerator = 0
        total_denominator = 0
        for child in node.children:
            child_achievement = calculate_achievement(child)
            total_numerator += child_achievement * child.contribution
            total_denominator += child.contribution

        # 貢献度が0の場合を考慮して分母が0でないことを確認してから達成度を計算
        if total_denominator == 0:
            return 0
        achievement = total_numerator / total_denominator
        return achievement

# 達成度の計算
overall_achievement = calculate_achievement(updated_root)
print("全体の達成度:", overall_achievement,excel_file)
print_tree(root_node)

