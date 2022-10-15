from dataclasses import dataclass

# y값이 반대! -> y축 계산시 부등호 반대로 해야
def collision_check(A, B):
    if A.top > B.bottom and B.top > A.bottom and A.left < B.right and B.left < A.right:
        return True
    else:
        return False