from django.urls import path
from . import views


app_name = 'contract'
urlpatterns = [
    path('contract', views.ContractListView.as_view(), name = 'view_contract'),
    path('contract/add', views.ContractCreate.as_view(), name = 'contract_create'),
    path('contract/edit/<int:pk>', views.ContractUpdateView.as_view(), name = 'contract_edit'),
    path('contract/delete/<int:pk>', views.ContractDeleteView.as_view(), name = 'contract_delete'),
    path('contract/add/sheet', views.add_multi_tracing_number, name='add_multiple_number')
]

urlpatterns += [
    path('order/<int:pk>', views.OrderDetailView.as_view(), name = 'order-detail'),
    path('order/add', views.OrderCreateView.as_view(), name = 'order_create'),
    path('order', views.OrderListView.as_view(), name = 'order-list'),
    path('<int:pk>/order', views.OrderbyContractListView.as_view(), name = 'partial-order-list'),
    path('order/edit/<int:pk>', views.OrderUpdateView.as_view(), name = 'order_edit'),
    path('order/delete/<int:pk>', views.OrderDeleteView.as_view(), name = 'order_delete'),
    path('<int:pk>/order/add', views.AddSpecifyContracttoOrder, name = 'add_specify_order'),
]

urlpatterns += [
    path('receipt', views.ReceiptListView.as_view(), name = 'receipt-list'),
    path('<int:pk>/receipt', views.ReceiptbyContract.as_view(), name = 'partial-receipt-list'),
    path('receipt/add', views.ReceiptCreateView.as_view(), name = 'receipt_create'),
    path('receipt/<int:pk>', views.ReceiptDetailView.as_view(), name = 'receipt-detail'),
    path('receipt/edit/<int:pk>', views.ReceiptUpdateView.as_view(), name = 'receipt_edit'),
    path('receipt/delete/<int:pk>', views.ReceiptDeleteView.as_view(), name = 'receipt_delete'),
    path('<int:pk>/receipt/add', views.AddSpecifyContracttoReceipt, name = 'add_specify_receipt'),
]

urlpatterns += [
    path('box/<int:pk>', views.BoxDetailView.as_view(), name = 'box-detail'),
    path('box/add', views.BoxCreateView.as_view(), name = 'box_create'),
    path('box', views.BoxListView.as_view(), name = 'box-list'),
    path('order/<int:pk>/box', views.BoxbyOrderListView.as_view(), name = 'partial-box-list'),
    path('box/edit/<int:pk>', views.BoxUpdateView, name = 'box_edit'),
    path('box/delete/<int:pk>', views.BoxDeleteView.as_view(), name = 'box_delete'),
    path('order/<int:pk>/box/add', views.AddSpecifyOrdertoBox, name = 'add_specify_box'),
]

urlpatterns += [
    path('failed', views.FailedListView.as_view(), name = 'failed-list'),
    path('failed/add', views.FailedCreateView.as_view(), name = 'failed_create'),
    path('failed/edit/<int:pk>', views.FailedUpdateView.as_view(), name = 'failed_edit'),
    path('failed/delete/<int:pk>', views.FailedDeleteView.as_view(), name = 'failed_delete'),
    path('box/<int:pk>/failed/add', views.AddSpecifyBoxtoFailed, name = 'add_specify_failed')
]

urlpatterns += [
    path('destroyed', views.DestroyedListView.as_view(), name = 'destroyed-list'),
    path('destroyed/add', views.DestroyedCreateView.as_view(), name = 'destroyed_create'),
    path('destroyed/<int:pk>', views.DestroyedDetailView.as_view(), name = 'destroyed-detail'),
    path('destroyed/delete/<int:pk>', views.DestroyedDeleteView.as_view(), name = 'destroyed_delete'),    
    path('destroyed/edit/<int:pk>', views.DestroyedUpdateView.as_view(), name = 'destroyed_edit'),
    path('box/<int:pk>/destroyed/add', views.AddSpecifyBoxtoDestroyed, name = 'add_specify_destroyed'),
]

urlpatterns += [
    path('failed_reason/<int:pk>', views.Failed_reasonDetailView.as_view(), name = 'failed_reason-detail'),
    path('failed_reason/add', views.Failed_reasonCreateView.as_view(), name = 'failed_reason_create'),
    path('failed_reason/edit/<int:pk>', views.Failed_reasonUpdateView.as_view(), name = 'failed_reason_edit'),
    path('failed_reason/delete/<int:pk>', views.Failed_reasonDeleteView.as_view(), name = 'failed_reason_delete'),
    path('failed_reason', views.Failed_reasonListView.as_view(), name = 'failed_reason-list'),    
]

urlpatterns += [
    path('examiner', views.ExaminerListView.as_view(), name = 'examiner-list'),
    path('examiner/edit/<int:pk>', views.ExaminerUpdateView.as_view(), name = 'examiner_edit'),
    path('examiner/add', views.ExaminerCreateView.as_view(), name = 'examiner_create'),
    path('examiner/delete/<int:pk>', views.ExaminerDeleteView.as_view(), name = 'examiner_delete'),
    path('box/<int:pk>/examiner/add', views.AddSpecifyBoxtoExaminer, name = 'add_specify_examiner'),
]

urlpatterns += [
    path('organization/add', views.add_organization, name = 'add_organization'),
]

urlpatterns += [
    path('payment_method/add', views.Payment_methodCreateView.as_view(), name = 'add_payment_method'),
    path('payment_method/edit/<int:pk>', views.Payment_methodUpdateView.as_view(), name = 'edit_payment_method'),
    path('payment_method/delete/<int:pk>', views.Payment_methodDeleteView.as_view(), name = 'delete_payment_method'),
    path('payment_method', views.Payment_methodListView.as_view(), name = 'payment_method-list'),
]

urlpatterns += [
    path('search', views.Search, name = 'search'),
]

urlpatterns += [
    path('upload/image/<int:pk>', views.Upload_image, name = 'upload_image'),
    path('upload/file/<int:pk>', views.Upload_file, name = 'upload_file'),
]

urlpatterns += [
    path('get/<model>/<int:pk>', views.update_element, name='update_element'),
]