! I am not so sure if 
subroutine calculate_esp(length_points, length_dens, eval_points, integration_points, integration_weights, density, esp) bind(C)
    use iso_c_binding
    implicit none

    integer(c_int), intent(in), value :: length_points, length_dens
    real(c_double), intent(in) :: eval_points(length_points*3), integration_points(length_dens*3), &
        integration_weights(length_dens), density(length_dens)
    real(c_double) :: eval_points_3D(3,length_points), integration_points_3D(3,length_dens), &
        distances_3D(3,length_dens), distances(length_dens)
    real(c_double), intent(out) :: esp(length_points)
    integer :: i,j
    real(c_double), parameter :: thres=1.e-5


    ! do i=1,length_points
    !     eval_points_3D(:,i)=eval_points(i*3-2:i*3)
    ! enddo
    ! do i=1,length_dens
    !     integration_points_3D(:,i)=integration_points(i*3-2:i*3)!, (/3,length_dens /))
    ! enddo
    
    eval_points_3D=reshape(eval_points, (/ 3, length_points/) )
    integration_points_3D=reshape(integration_points, (/ 3, length_dens /) )

    ! Distances
    do i=1,length_points
        do j=1,length_dens
            distances_3D(:,j)=integration_points_3D(:,j)-eval_points_3D(:,i)
        enddo
        distances=sqrt( distances_3D(1,:)**2 + distances_3D(2,:)**2 + distances_3D(3,:)**2 )
        do j=1,length_dens
            if ( abs(distances(j)) < thres ) then
                distances(j)=0._c_double
            else
                distances(j)=1_c_double/distances(j)
            endif
        enddo
        esp(i)=dot_product(distances,integration_weights*density)

        ! esp(:)=abs(distances)
        !where ( abs(distances) < 1.e-5_c_double )
        !    distances=0.0_c_double
        !elsewhere
        !    distances=1_c_double/distances(j)
        !endwhere
    enddo

    
end subroutine calculate_esp


!  function average(v, count) bind(C)
!      use iso_c_binding
!      implicit none
!  
!      integer(c_int), intent(in), value :: count
!      real(c_double), intent(in) :: v(count)
!      real(c_double) :: average
!      integer(c_int) :: i
!  
!      average = 0.0d0
!      do i = 1 , count
!        average = average + v(i)
!      end do
!  
!      average=v(100)
!      print *, average
!      average = average / count
!  end function average
