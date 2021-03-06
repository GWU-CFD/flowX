"""Routine to compute the predictor, corrector, and divergence."""

import numpy

from flowx.ins.solvers.operators import diffusion, convective_facex, convective_facey

def predictor(gridc, gridx, gridy, ivar, hvar, pres, Re, ifac, ipres):
    """Velocity prediction step in x and y direction.

    Arguments
    ---------
    gridx : grid object (x-direction)
        Grid containing data in x-direction.
    gridy : grid object (y-direction)
        Grid containing data in y-direction.
    ivar : string
        Name of the grid variable of the velocity solution.
    hvar : string
        Name of the grid variable to store convective + diffusion terms.
    Re : float
        Reynolds number.
    ifac : float
        Time-step size.

    """
    hx = gridx.get_values(hvar)
    hy = gridy.get_values(hvar)

    dx, dy = gridx.dx, gridy.dy

    p = gridc.get_values(pres)

    hx[1:-1, 1:-1] = (convective_facex(gridx, gridy, ivar) +
                      diffusion(gridx, ivar, 1 / Re))
    hy[1:-1, 1:-1] = (convective_facey(gridx, gridy, ivar) +
                      diffusion(gridy, ivar, 1 / Re))

    u = gridx.get_values(ivar)
    v = gridy.get_values(ivar)

    u[1:-1, 1:-1] = u[1:-1, 1:-1] + ifac * hx[1:-1, 1:-1] - ifac * ipres * (p[2:-1, 1:-1] - p[1:-2, 1:-1]) / dx
    v[1:-1, 1:-1] = v[1:-1, 1:-1] + ifac * hy[1:-1, 1:-1] - ifac * ipres * (p[1:-1, 2:-1] - p[1:-1, 1:-2]) / dy

    return

def predictor_AB2(gridc, gridx, gridy, ivar, hvar, pres, Re, ifac, ipres):
    """Velocity prediction step in x and y direction.

    Arguments
    ---------
    gridx : grid object (x-direction)
        Grid containing data in x-direction.
    gridy : grid object (y-direction)
        Grid containing data in y-direction.
    ivar : string
        Name of the grid variable of the velocity solution.
    hvar : string
        Name of the grid variable to store convective + diffusion terms.
    Re : float
        Reynolds number.
    ifac : float
        Time-step size.

    """
    hx_old = gridx.get_values(hvar)
    hy_old = gridy.get_values(hvar)

    dx, dy = gridx.dx, gridy.dy

    p = gridc.get_values(pres)

    hx_new = (convective_facex(gridx, gridy, ivar) +
                      diffusion(gridx, ivar, 1 / Re)) 
    hy_new = (convective_facey(gridx, gridy, ivar) +
                      diffusion(gridy, ivar, 1 / Re)) 

    u = gridx.get_values(ivar)
    v = gridy.get_values(ivar)

    u[1:-1, 1:-1] = u[1:-1, 1:-1] + ifac * (1.5 * hx_new - 0.5 * hx_old[1:-1, 1:-1]) \
                                  - ifac * ipres * (p[2:-1, 1:-1] - p[1:-2, 1:-1]) / dx

    v[1:-1, 1:-1] = v[1:-1, 1:-1] + ifac * (1.5 * hy_new - 0.5 * hy_old[1:-1, 1:-1]) \
                                  - ifac * ipres * (p[1:-1, 2:-1] - p[1:-1, 1:-2]) / dy
 
    hx_old[1:-1,1:-1] = hx_new
    hy_old[1:-1,1:-1] = hy_new

    return

def predictor_RK3(gridc, gridx, gridy, ivar, hvar, pres, Re, ifac, ipres, hconst):
    """Velocity prediction step in x and y direction.

    Arguments
    ---------
    gridx : grid object (x-direction)
        Grid containing data in x-direction.
    gridy : grid object (y-direction)
        Grid containing data in y-direction.
    ivar : string
        Name of the grid variable of the velocity solution.
    hvar : string
        Name of the grid variable to store convective + diffusion terms.
    Re : float
        Reynolds number.
    ifac : float
        Time-step size.

    """
    hx = gridx.get_values(hvar)
    hy = gridy.get_values(hvar)

    dx, dy = gridx.dx, gridy.dy

    p = gridc.get_values(pres)

    hx[1:-1, 1:-1] = (convective_facex(gridx, gridy, ivar) +
                      diffusion(gridx, ivar, 1 / Re)) + hconst * hx[1:-1,1:-1]
    hy[1:-1, 1:-1] = (convective_facey(gridx, gridy, ivar) +
                      diffusion(gridy, ivar, 1 / Re)) + hconst * hy[1:-1,1:-1]

    u = gridx.get_values(ivar)
    v = gridy.get_values(ivar)

    u[1:-1, 1:-1] = u[1:-1, 1:-1] + ifac * hx[1:-1, 1:-1]
    v[1:-1, 1:-1] = v[1:-1, 1:-1] + ifac * hy[1:-1, 1:-1]

    return

def divergence(gridc, gridx, gridy, ivar, dvar, ifac=1.0):
    """Compute the divergence of the variable tagged "ivar".

    Arguments
    ---------
    gridc : grid object
        Grid containing data in on cell centers.
    gridx : grid object (x-direction)
        Grid containing data in x-direction.
    gridy : grid object (y-direction)
        Grid containing data in y-direction.
    ivar : string
        Name of the face-centered grid variable for velocity.
    dvar : string
        Name of the cell-centered grid variable to store divergence.
    ifac : float (optional)
        Multiplying factor for time-step; default: 1.0.

    """
    u = gridx.get_values(ivar)
    v = gridy.get_values(ivar)

    div = gridc.get_values(dvar)

    dx, dy = gridc.dx, gridc.dy

    div[1:-1, 1:-1] = ((u[1:, 1:-1] - u[:-1, 1:-1]) / dx +
                       (v[1:-1, 1:] - v[1:-1, :-1]) / dy) / ifac

    return

def corrector(gridc, gridx, gridy, ivar, pvar, delp, ifac, ipres):
    """Velocity correction in x and y direction.

    Arguments
    ---------
    gridc : grid object (cell center)
        Grid contaning data in cell center.
    gridx : grid object (x-direction)
        Grid containing data in x-direction.
    gridy : grid object  (y-direction)
        Grid containing data in y-direction.
    ivar : string
        Name of the grid variable of the velocity solution.
    pvar : string
        Name of the grid variable of the pressure solution.
    ifac : float
        Time-step size.

    """
    u = gridx.get_values(ivar)
    v = gridy.get_values(ivar)
    p = gridc.get_values(pvar)
    dp = gridc.get_values(delp)

    dx, dy = gridx.dx, gridy.dy

    u[:,:] = u[:, :] - ifac * (dp[1:, :] - dp[:-1, :]) / dx
    v[: :] = v[:, :] - ifac * (dp[:, 1:] - dp[:, :-1]) / dy

    p[:,:] = ipres*p[:,:] + dp[:,:]

    return
