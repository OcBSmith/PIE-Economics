using Test
using MacroAIComp

@testset "Tobin's Q Tests" begin
    @testset "Steady State" begin
        params = default_calibration(TobinQParams)
        ss = compute_steady_state(params)

        @test ss["q"] ≈ 1.0 atol=1e-6
        @test ss["K"] ≈ 6.8711236 atol=1e-6
        @test ss["I"] ≈ 0.06 * 6.8711236 atol=1e-6
        @test ss["Y"] ≈ 6.8711236^0.35 atol=1e-6
    end

    @testset "Eigenvalues Saddle Point" begin
        params = default_calibration(TobinQParams)
        lin_sys = compute_linearized_system(params)

        lambda_1 = lin_sys["lambda_1"]
        lambda_2 = lin_sys["lambda_2"]

        @test lambda_1 < 0.0
        @test lambda_2 > 0.0

        @test lambda_1 ≈ -0.060658 atol=1e-5
        @test lambda_2 ≈ 0.107158 atol=1e-5

        @test (1.0 + lambda_1) ≈ 0.939342 atol=1e-5
        @test (1.0 + lambda_2) ≈ 1.107158 atol=1e-5

        @test abs(1.0 + lambda_1) < 1.0
        @test abs(1.0 + lambda_2) > 1.0
    end

    @testset "Jump Formula Identity" begin
        # Test under different calibrations to ensure identity holds generally
        for R_val in [0.02, 0.03, 0.04, 0.05]
            for phi_val in [5.0, 10.0, 15.0]
                params = TobinQParams(0.35, 0.06, phi_val, R_val)
                lin_sys = compute_linearized_system(params)

                @test lin_sys["theta"] ≈ lin_sys["theta_book"] atol=1e-12
            end
        end
    end

    @testset "Simulation Interest Rate Shock" begin
        params = default_calibration(TobinQParams)
        T = 100

        # Initial steady state capital at R = 4%
        ss_init = compute_steady_state(params, 0.04)
        K0 = ss_init["K"]

        # Permanent shock to R: 4% at t=0 (index 1 in Julia), drops to 3% for t >= 2
        R_path = zeros(T)
        R_path[1] = 0.04
        R_path[2:end] .= 0.03

        # Solve using both solvers
        res_lin = solve_linearized_simulation(params, K0, R_path, T)
        res_nonlin = solve_nonlinear_simulation(params, K0, R_path, T)

        # 1. Predetermined capital stock: K[1] = K0 in both simulations
        @test res_lin["K"][1] ≈ K0 atol=1e-12
        @test res_nonlin["K"][1] ≈ K0 atol=1e-12

        # 2. Convergence to new steady state (R = 3%)
        ss_final = compute_steady_state(params, 0.03)
        K_ss_final = ss_final["K"]

        @test res_lin["K"][end] ≈ K_ss_final atol=5e-3
        @test res_nonlin["K"][end] ≈ K_ss_final atol=5e-3

        # 3. Q ratio dynamics: jumps above 1.0 initially, then converges back to 1.0
        @test res_lin["q"][1] > 1.0
        @test res_nonlin["q"][1] > 1.0
        @test res_lin["q"][1] ≈ 1.1033 atol=1e-4

        @test res_lin["q"][end] ≈ 1.0 atol=1e-3
        @test res_nonlin["q"][end] ≈ 1.0 atol=1e-3

        # 4. Consistency: linearized and non-linear simulation should be very close
        @test res_lin["K"] ≈ res_nonlin["K"] rtol=1e-2
        @test res_lin["q"] ≈ res_nonlin["q"] rtol=1e-2
    end
end
