from rotax_infrastructure import GoBoard, my_add

print(f"test from rust: {my_add(1,2)}")
A = GoBoard(19, [1,2,3,4])
print(A,A.size)
A.change_size(9)
print(A.size)

print(A.block_liberty)

A.block_liberty.append(1)
print(A.block_liberty)

A.change_liberty([4,3,2,1,0])
print(A.block_liberty)
