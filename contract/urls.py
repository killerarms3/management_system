from django.urls import path
from . import views


app_name = 'contract'
urlpatterns = [
    path('contracts/', views.ContractListView.as_view(), name = 'view_contract'),
    path('contracts/create', views.ContractCreate.as_view(), name = 'contract_create'),
    path('contracts/<int:pk>/edit', views.ContractUpdateView.as_view(), name = 'contract_edit'),
    path('contracts/<int:pk>/delete', views.ContractDeleteView.as_view(), name = 'contract_delete'),
]

urlpatterns += [
    path('order/<int:pk>', views.OrderDetailView.as_view(), name = 'order-detail'),    
    path('order/add', views.OrderCreateView.as_view(), name = 'order_create'),
    path('order/order_list', views.OrderListView.as_view(), name = 'order-list'),
    path('order/order_list/<int:pk>', views.OrderbyContractListView.as_view(), name = 'partial-order-list'),
    path('order/<int:pk>/edit', views.OrderUpdateView.as_view(), name = 'order_edit'),
    path('order/<int:pk>/delete', views.OrderDeleteView.as_view(), name = 'order_delete'),
    path('order/<int:pk>/add', views.AddSpecifyContracttoOrder, name = 'add_specify_order'),
]

urlpatterns += [
    path('receipt/receipt_list', views.ReceiptListView.as_view(), name = 'receipt-list'),
    path('receipt/receipt_list/<int:pk>', views.ReceiptbyContract.as_view(), name = 'partial-receipt-list'),
    path('receipt/add', views.ReceiptCreateView.as_view(), name = 'receipt_create'),
    path('receipt/<int:pk>', views.ReceiptDetailView.as_view(), name = 'receipt-detail'),
    path('receipt/<int:pk>/edit', views.ReceiptUpdateView.as_view(), name = 'receipt_edit'),
    path('receipt/<int:pk>/delete', views.ReceiptDeleteView.as_view(), name = 'receipt_delete'),
    path('receipt/<int:pk>/add', views.AddSpecifyContracttoReceipt, name = 'add_specify_receipt'),
]

urlpatterns += [
    path('box/<int:pk>', views.BoxDetailView.as_view(), name = 'box-detail'),
    path('box/add', views.BoxCreateView.as_view(), name = 'box_create'),
    path('box/add/sheet', views.add_multi_box, name = 'add_multi_box'),
    path('box/box_list', views.BoxListView.as_view(), name = 'box-list'),
    path('box/box_list/<int:pk>', views.BoxbyOrderListView.as_view(), name = 'partial-box-list'),
    path('box/<int:pk>/edit', views.BoxUpdateView, name = 'box_edit'),
    path('box/<int:pk>/delete', views.BoxDeleteView.as_view(), name = 'box_delete'),
    path('box/<int:pk>/add', views.AddSpecifyOrdertoBox, name = 'add_specify_box'),
]

urlpatterns += [
    path('box/failed_box_list/', views.FailedListView.as_view(), name = 'failed-list'),
    path('box/failed_box_list/add', views.FailedCreateView.as_view(), name = 'failed_create'),
    path('box/failed_box/<int:pk>/edit', views.FailedUpdateView.as_view(), name = 'failed_edit'),
    path('box/failed_box/<int:pk>/delete', views.FailedDeleteView.as_view(), name = 'failed_delete'),
    path('box/failed_box/<int:pk>/add', views.AddSpecifyBoxtoFailed, name = 'add_specify_failed')
]

urlpatterns += [
    path('box/destroyed_box_list/', views.DestroyedListView.as_view(), name = 'destroyed-list'),
    path('box/destroyed_box_list/add', views.DestroyedCreateView.as_view(), name = 'destroyed_create'),
    path('box/destroyed_box/<int:pk>', views.DestroyedDetailView.as_view(), name = 'destroyed-detail'),
    path('box/destroyed_box/<int:pk>/delete', views.DestroyedDeleteView.as_view(), name = 'destroyed_delete'),    
    path('box/destroyed_box/<int:pk>/edit', views.DestroyedUpdateView.as_view(), name = 'destroyed_edit'),
    path('box/destroyed_box/<int:pk>/add', views.AddSpecifyBoxtoDestroyed, name = 'add_specify_destroyed'),
]

urlpatterns += [
    path('failed_reason/<int:pk>', views.Failed_reasonDetailView.as_view(), name = 'failed_reason-detail'),
    path('failed_reason/add', views.Failed_reasonCreateView.as_view(), name = 'failed_reason_create'),
    path('failed_reason/<int:pk>/edit', views.Failed_reasonUpdateView.as_view(), name = 'failed_reason_edit'),
    path('failed_reason/<int:pk>/delete', views.Failed_reasonDeleteView.as_view(), name = 'failed_reason_delete'),
    path('failed_reason-list/', views.Failed_reasonListView.as_view(), name = 'failed_reason-list'),    
]

urlpatterns += [
    path('examiner_list', views.ExaminerListView.as_view(), name = 'examiner-list'),
    path('examiner/<int:pk>/edit', views.ExaminerUpdateView.as_view(), name = 'examiner_edit'),
    path('examiner/add', views.ExaminerCreateView.as_view(), name = 'examiner_create'),
    path('examiner/<int:pk>/delete', views.ExaminerDeleteView.as_view(), name = 'examiner_delete'),
    path('examiner/<int:pk>/add', views.AddSpecifyBoxtoExaminer, name = 'add_specify_examiner'),
]

urlpatterns += [
    path('add_organization', views.add_organization, name = 'add_organization'),
]

urlpatterns += [
    path('add_payment_method', views.Payment_methodCreateView.as_view(), name = 'add_payment_method'),
    path('edit_payment_method/<int:pk>', views.Payment_methodUpdateView.as_view(), name = 'edit_payment_method'),
    path('delete_payment_method/<int:pk>', views.Payment_methodDeleteView.as_view(), name = 'delete_payment_method'),
    path('payment_method_list', views.Payment_methodListView.as_view(), name = 'payment_method-list'),
]

urlpatterns += [
    path('search', views.Search, name = 'search'),
]

urlpatterns += [
    path('upload/image/<int:pk>', views.Upload_image, name = 'upload_image'),
    path('upload/file/<int:pk>', views.Upload_file, name = 'upload_file'),
]

urlpatterns += [
    path('update_element/<model>/<int:pk>', views.update_element, name='update_element'),
]